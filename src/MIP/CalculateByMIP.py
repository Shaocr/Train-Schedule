from __future__ import print_function

import collections
from ortools.sat.python import cp_model
import plotly as py
import plotly.figure_factory as ff

pyplt = py.offline.plot


class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__solution_count = 0

    def on_solution_callback(self):
        """Called at each new solution."""
        print('Solution %i, time = %f s, objective = %i' %
              (self.__solution_count, self.WallTime(), self.ObjectiveValue()))
        self.__solution_count += 1


def gatt(machine_task):
    '''
    :param machine_task: Both start time and finish time of all tasks which are performed on definite machine
    :return:None
    '''
    df = []
    for i in range(len(machine_task)):
        for j in range(len(machine_task[i])):
            df.append(
                dict(Task='Machine %s' % (i), Start='2018-07-%s' % (str(machine_task[i][j]['Start'] + 1).zfill(2)),
                     Finish='2018-07-%s' % (str(machine_task[i][j]['Finish'] + 1).zfill(2)),
                     Resource=machine_task[i][j]['Task']))
    print(df)
    fig = ff.create_gantt(df, index_col='Resource', show_colorbar=True, group_tasks=True, showgrid_x=True,
                          title='Job shop Schedule')
    pyplt(fig, filename='1.html')



def Solve(MachineNum, jobs):
    '''
    Args:
        :param MachineNum: The number of machine which are used to work
        :param jobs: The time cost of every task on different machine
    Example:
        MachineNum:3
        jobs:[[[(3, 0), (1, 1), (5, 2)], [(2, 0), (4, 1), (6, 2)], [(2, 0), (3, 1), (1, 2)]],
            [[(2, 0), (3, 1), (4, 2)], [(1, 0), (5, 1), (4, 2)], [(2, 0), (1, 1), (4, 2)]],
            [[(2, 0), (1, 1), (4, 2)], [(2, 0), (3, 1), (4, 2)], [(3, 0), (1, 1), (5, 2)]]
            ]

    :return: machine_task
    '''
    num_jobs = len(jobs)
    all_jobs = range(num_jobs)

    num_machines = MachineNum
    all_machines = range(num_machines)

    # Model the flexible jobshop problem.
    model = cp_model.CpModel()

    horizon = 0
    for job in jobs:
        for task in job:
            max_task_duration = 0
            for alternative in task:
                max_task_duration = max(max_task_duration, alternative[0])
            horizon += max_task_duration

    print('Horizon = %i' % horizon)

    # Global storage of variables.
    intervals_per_resources = collections.defaultdict(list)
    starts = {}  # indexed by (job_id, task_id).
    presences = {}  # indexed by (job_id, task_id, alt_id).
    job_ends = []

    # Scan the jobs and create the relevant variables and intervals.
    for job_id in all_jobs:
        job = jobs[job_id]
        num_tasks = len(job)
        previous_end = None
        for task_id in range(num_tasks):
            task = job[task_id]

            min_duration = task[0][0]
            max_duration = task[0][0]

            num_alternatives = len(task)
            all_alternatives = range(num_alternatives)

            for alt_id in range(1, num_alternatives):
                alt_duration = task[alt_id][0]
                min_duration = min(min_duration, alt_duration)
                max_duration = max(max_duration, alt_duration)

            # Create main interval for the task.
            suffix_name = '_j%i_t%i' % (job_id, task_id)
            start = model.NewIntVar(0, horizon, 'start' + suffix_name)
            duration = model.NewIntVar(min_duration, max_duration,
                                       'duration' + suffix_name)
            end = model.NewIntVar(0, horizon, 'end' + suffix_name)
            interval = model.NewIntervalVar(start, duration, end,
                                            'interval' + suffix_name)

            # Store the start for the solution.
            starts[(job_id, task_id)] = start

            # Add precedence with previous task in the same job.
            if previous_end:
                model.Add(start >= previous_end)
            previous_end = end

            # Create alternative intervals.
            if num_alternatives > 1:
                l_presences = []
                for alt_id in all_alternatives:
                    alt_suffix = '_j%i_t%i_a%i' % (job_id, task_id, alt_id)
                    l_presence = model.NewBoolVar('presence' + alt_suffix)
                    l_start = model.NewIntVar(0, horizon, 'start' + alt_suffix)
                    l_duration = task[alt_id][0]
                    l_end = model.NewIntVar(0, horizon, 'end' + alt_suffix)
                    l_interval = model.NewOptionalIntervalVar(
                        l_start, l_duration, l_end, l_presence,
                        'interval' + alt_suffix)
                    l_presences.append(l_presence)

                    # Link the master variables with the local ones.
                    model.Add(start == l_start).OnlyEnforceIf(l_presence)
                    model.Add(duration == l_duration).OnlyEnforceIf(l_presence)
                    model.Add(end == l_end).OnlyEnforceIf(l_presence)

                    # Add the local interval to the right machine.
                    intervals_per_resources[task[alt_id][1]].append(l_interval)

                    # Store the presences for the solution.
                    presences[(job_id, task_id, alt_id)] = l_presence

                # Select exactly one presence variable.
                model.Add(sum(l_presences) == 1)
            else:
                intervals_per_resources[task[0][1]].append(interval)
                presences[(job_id, task_id, 0)] = model.NewConstant(1)

        job_ends.append(previous_end)

    # Create machines constraints.
    for machine_id in all_machines:
        intervals = intervals_per_resources[machine_id]
        if len(intervals) > 1:
            model.AddNoOverlap(intervals)

    # Makespan objective
    makespan = model.NewIntVar(0, horizon, 'makespan')
    model.AddMaxEquality(makespan, job_ends)
    model.Minimize(makespan)

    # Solve model.
    solver = cp_model.CpSolver()
    solution_printer = SolutionPrinter()
    status = solver.SolveWithSolutionCallback(model, solution_printer)
    OptimizationResult = solver.ObjectiveValue()
    machine_task = [[] for i in range(num_machines)]
    job_task = [['job%i'%(i),[],[]] for i in range(num_jobs)]
    # Print final solution.
    for job_id in all_jobs:
        print('Job %i:' % job_id)
        num_tasks = len(jobs[job_id])
        for task_id in range(len(jobs[job_id])):
            start_value = solver.Value(starts[(job_id, task_id)])
            machine = -1
            duration = -1
            selected = -1
            for alt_id in range(len(jobs[job_id][task_id])):
                if solver.Value(presences[(job_id, task_id, alt_id)]):
                    duration = jobs[job_id][task_id][alt_id][0]
                    machine = jobs[job_id][task_id][alt_id][1]
                    selected = alt_id
            print(
                '  task_%i_%i starts at %i (alt %i, machine %i, duration %i)' %
                (job_id, task_id, start_value, selected, machine, duration))
            machine_task[machine].append(
                dict(Task='%i' % (job_id + 1), Start=start_value, Finish=start_value + duration))
            job_task[job_id][2].append(start_value)
            job_task[job_id][2].append(start_value+duration)
            job_task[job_id][1].append(num_tasks)
            job_task[job_id][1].append(num_tasks - 1)
            num_tasks-=1
    # print('Solve status: %s' % solver.StatusName(status))
    # print('Optimal objective value: %i' % solver.ObjectiveValue())
    # print('Statistics')
    # print('  - conflicts : %i' % solver.NumConflicts())
    # print('  - branches  : %i' % solver.NumBranches())
    # print('  - wall time : %f s' % solver.WallTime())
    # gatt(machine_task)
    return (OptimizationResult,job_task,machine_task)
if __name__ == '__main__':
    jobs = [[[(3, 0), (1, 1), (5, 2)], [(2, 0), (4, 1), (6, 2)], [(2, 0), (3, 1), (1, 2)]],
            [[(2, 0), (3, 1), (4, 2)], [(1, 0), (5, 1), (4, 2)], [(2, 0), (1, 1), (4, 2)]],
            [[(2, 0), (1, 1), (4, 2)], [(2, 0), (3, 1), (4, 2)], [(3, 0), (1, 1), (5, 2)]]
            ]
    Solve(3, jobs)
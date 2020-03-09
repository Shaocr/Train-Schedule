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



def Solve(ScheduleData):
    '''
    Args:
        ScheduleData: The data of schedule,contains the number of machine and every task's time cost

    Explanation:

        ScheduleData->data:{MachinesNb:{int}  Explanation:The Number of Machines which are used to work
                            jobs:[...]        Explanation:The data of time cost of jobs on different machines}

        ScheduleData->data->jobs:[job1[...],job2[...],...]
        ScheduleData->data->jobs->job:[task1[...],task2[...],...]
        ScheduleData->data->jobs->job->task:[{machine:{int},processingTime:{int}},...]

    Example:
        ScheduleData={'machinesNb':3,
                        'jobs':[
                            [[{'machine':1,'processingTime':4}],[{'machine':3,'processingTime':4}]],
                            [[{'machine':1,'processingTime':5}],[{'machine':2,'processingTime':4}]]
                        ]}
    Return:
        start_time: The start time of every task
        finish_time: The Finish time of every task
    '''
    jobs = ScheduleData['jobs']
    num_jobs = len(jobs)
    all_jobs = range(num_jobs)

    num_machines = ScheduleData['machinesNb']
    all_machines = range(num_machines)

    # Model the flexible jobshop problem.
    model = cp_model.CpModel()

    horizon = 0
    for job in jobs:
        for task in job:
            max_task_duration = 0
            for alternative in task:
                max_task_duration = max(max_task_duration, alternative['processingTime'])
            horizon += max_task_duration

    print('Horizon = %i' % horizon)

    # Global storage of variables.
    intervals_per_resources = collections.defaultdict(list)
    starts = {}  # indexed by (job_id, task_id).
    presences = {}  # indexed by (job_id, task_id, alt_id).
    job_ends = []
    # Named tuple to store information about created variables.
    task_type = collections.namedtuple('Task', 'start end leave occupy')
    # Creates job intervals and add to the corresponding machine lists.
    all_tasks = {}
    # Scan the jobs and create the relevant variables and intervals.
    for job_id in all_jobs:
        job = jobs[job_id]
        num_tasks = len(job)
        previous_end = None
        for task_id in range(num_tasks):
            task = job[task_id]

            min_duration = task[0]['processingTime']
            max_duration = task[0]['processingTime']

            num_alternatives = len(task)
            all_alternatives = range(num_alternatives)

            for alt_id in range(1, num_alternatives):
                alt_duration = task[alt_id]['processingTime']
                min_duration = min(min_duration, alt_duration)
                max_duration = max(max_duration, alt_duration)

            # Create main interval for the task.
            suffix_name = '_j%i_t%i' % (job_id, task_id)
            start = model.NewIntVar(0, horizon, 'start' + suffix_name)
            duration = model.NewIntVar(min_duration, max_duration,
                                       'duration' + suffix_name)
            end = model.NewIntVar(0, horizon, 'end' + suffix_name)
            time_occupy = model.NewIntVar(min_duration,horizon,'occupy'+suffix_name)
            leave_val = model.NewIntVar(0, horizon, 'leave' + suffix_name)
            interval = model.NewIntervalVar(start, time_occupy, leave_val,
                                            'interval' + suffix_name)

            all_tasks[job_id, task_id] = task_type(
                start=start, end=end, leave=leave_val, occupy=time_occupy)
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
                    l_duration = task[alt_id]['processingTime']
                    l_end = model.NewIntVar(0, horizon, 'end' + alt_suffix)
                    l_time_occupy = model.NewIntVar(l_duration, horizon, 'occupy' + alt_suffix)
                    l_leave_val = model.NewIntVar(0, horizon, 'leave' + alt_suffix)
                    l_interval = model.NewOptionalIntervalVar(
                        l_start, l_time_occupy, l_leave_val, l_presence,
                        'interval' + alt_suffix)
                    l_presences.append(l_presence)

                    # Link the master variables with the local ones.
                    model.Add(start == l_start).OnlyEnforceIf(l_presence)
                    model.Add(duration == l_duration).OnlyEnforceIf(l_presence)
                    model.Add(end == l_end).OnlyEnforceIf(l_presence)

                    # Add the local interval to the right machine.
                    intervals_per_resources[task[alt_id]['machine']].append(l_interval)

                    # Store the presences for the solution.
                    presences[(job_id, task_id, alt_id)] = l_presence

                # Select exactly one presence variable.
                model.Add(sum(l_presences) == 1)
            else:
                intervals_per_resources[task[0]['machine']].append(interval)
                presences[(job_id, task_id, 0)] = model.NewConstant(1)

        job_ends.append(previous_end)


    for job_id,job in enumerate(jobs):
        for task_id in range(0,len(job)-1):
            model.Add(all_tasks[job_id, task_id].leave == all_tasks[job_id, task_id+1].start)
            model.Add(all_tasks[job_id, task_id].occupy == all_tasks[job_id, task_id].leave-all_tasks[job_id, task_id].start)
        model.Add(all_tasks[job_id,len(job)-1].leave==all_tasks[job_id,len(job)-1].end)
        model.Add(all_tasks[job_id, len(job)-1].occupy == all_tasks[job_id, len(job)-1].end - all_tasks[job_id, len(job)-1].start)

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
    job_task = [['train%i'%(i+1),[],[]] for i in range(num_jobs)]
    # Print final solution.
    for job_id in all_jobs:
        print('Job %i:' % job_id)
        num_tasks = len(jobs[job_id])
        direction_flag=False
        if jobs[job_id][0][0]['machine']!=0:
            direction_flag=True
        for task_id in range(len(jobs[job_id])):
            start_value = solver.Value(starts[(job_id, task_id)])
            machine = -1
            duration = -1
            selected = -1
            for alt_id in range(len(jobs[job_id][task_id])):
                if solver.Value(presences[(job_id, task_id, alt_id)]):
                    duration = jobs[job_id][task_id][alt_id]['processingTime']
                    machine = jobs[job_id][task_id][alt_id]['machine']
                    selected = alt_id
            print(
                '  task_%i_%i starts at %i (alt %i, machine %i, duration %i)' %
                (job_id, task_id, start_value, selected, machine, duration))
            # machine_task[machine-1].append(
            #     dict(Task='%i' % (job_id + 1), Start=start_value, Finish=start_value + duration))
            machine_task[machine - 1].append(
                ('%i-%i' % (job_id,task_id+1),duration, start_value,start_value))
            job_task[job_id][2].append(start_value)
            job_task[job_id][2].append(start_value+duration)
            if direction_flag:
                job_task[job_id][1].append(num_tasks-1-machine)
                job_task[job_id][1].append(num_tasks-machine)
            else:
                job_task[job_id][1].append(num_tasks-machine)
                job_task[job_id][1].append(num_tasks-machine-1)
    # print('Solve status: %s' % solver.StatusName(status))
    # print('Optimal objective value: %i' % solver.ObjectiveValue())
    # print('Statistics')
    # print('  - conflicts : %i' % solver.NumConflicts())
    # print('  - branches  : %i' % solver.NumBranches())
    # print('  - wall time : %f s' % solver.WallTime())
    # gatt(machine_task)
    return (OptimizationResult,job_task,machine_task)
if __name__ == '__main__':
    # jobs = [[[(3, 0), (1, 1), (5, 2)], [(2, 0), (4, 1), (6, 2)], [(2, 0), (3, 1), (1, 2)]],
    #         [[(2, 0), (3, 1), (4, 2)], [(1, 0), (5, 1), (4, 2)], [(2, 0), (1, 1), (4, 2)]],
    #         [[(2, 0), (1, 1), (4, 2)], [(2, 0), (3, 1), (4, 2)], [(3, 0), (1, 1), (5, 2)]]
    #         ]
    ScheduleData = {'machinesNb': 3,
                    'jobs': [
                        [[{'machine': 1, 'processingTime': 4}], [{'machine': 3, 'processingTime': 4}]],
                        [[{'machine': 1, 'processingTime': 5}], [{'machine': 2, 'processingTime': 4}]]
                    ]}
    Solve(ScheduleData)

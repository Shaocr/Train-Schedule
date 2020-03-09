'''
@author:Shaocr
@Date:2019-10-10
@Description:Solve the optimization problem of train schedule
'''
import time
import copy
from GA.utils import parser, gantt
from GA.genetic import encoding, decoding, genetic, termination
from GA import config
from GA.utils.Improve import CheckConflict,RepairConflict,SortSchedule

def Solve(ScheduleData,pr=0,pc=0,pm=0):
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

    average_all = ['Genetic', [], []]
    if pr != 0 :
        config.pr = pr
        config.pc = pc
        config.pm = pm
        if pc == 0.9:
            average_all[0] = 'FJSP'
        else:
            average_all[0] = 'FJSP-IV'
    #population = parser.parse('test_data/Brandimarte_Data/Text/Mk02.fjs')
    t0 = time.time()

    # Initialize the Population
    population = encoding.initializePopulation(ScheduleData)
    gen = 1

    gbest = 10000000000
    #best = ['best',[],[]]

    # Evaluate the population
    while not termination.shouldTerminate(population, gen):
        # Genetic Operators
        population = genetic.selection(population, ScheduleData)
        population = genetic.crossover(population, ScheduleData)
        population = genetic.mutation(population, ScheduleData)
        sortedPop = sorted(population, key=lambda cpl: genetic.timeTaken(cpl, ScheduleData))

        #pbest = genetic.timeTaken(sortedPop[0],ScheduleData)
        #if gbest > pbest:
            #gbest = pbest
        #best[1].append(gbest)
        #best[2].append(gen)
        sum_time = 0
        for i in sortedPop:
            sum_time += genetic.timeTaken(i,ScheduleData)
        average_all[1].append(sum_time/len(sortedPop))
        average_all[2].append(gen)
        print(gen,sum_time/len(sortedPop))
        gen = gen + 1


    sortedPop = sorted(population, key=lambda cpl: genetic.timeTaken(cpl, ScheduleData))

    t1 = time.time()
    total_time = t1 - t0
    print("Finished in {0:.2f}s".format(total_time))

    # Termination Criteria Satisfied ?
    gantt_data = decoding.translate_decoded_to_gantt(decoding.decode(ScheduleData, sortedPop[0][0], sortedPop[0][1]))
    job_task = [['train%i' % (i + 1), [], []] for i in range(len(ScheduleData['jobs']))]
    plot_data = decoding.translate_decoded_to_plot(decoding.decode(ScheduleData, sortedPop[0][0], sortedPop[0][1]),job_task)
    optimal = max([max(i[2]) for i in plot_data])
    scheduledata=[]
    for i in range(len(sortedPop)):
        scheduledata = SortSchedule(decoding.decode(ScheduleData, sortedPop[i][0], sortedPop[i][1]))
        if CheckConflict(scheduledata):
            break
    #scheduledata = SortSchedule(decoding.decode(ScheduleData,sortedPop[0][0],sortedPop[0][1]))
    print(CheckConflict(scheduledata))
    #scheduledata,process=RepairConflict(scheduledata)
    print(CheckConflict(scheduledata))
    job_task = [['train%i' % (i + 1), [], []] for i in range(len(ScheduleData['jobs']))]
    plot_data_repair = decoding.translate_decoded_to_plot(scheduledata,job_task)
    print(scheduledata)
    best = [average_all]
    process=[]
    return (optimal,plot_data,gantt_data,best,plot_data_repair,process)
    # if config.latex_export:
    #     gantt.export_latex(gantt_data)
    # else:
    #     gantt.draw_chart(gantt_data)


if __name__ == "__main__":
    ScheduleData = {'machinesNb': 3,
                    'jobs': [
                        [[{'machine': 1, 'processingTime': 4}], [{'machine': 3, 'processingTime': 4}]],
                        [[{'machine': 1, 'processingTime': 5}], [{'machine': 2, 'processingTime': 4}]]
                    ]}

    Solve(ScheduleData)

from PyQt5.QtCore import QPoint, QSize, QRect

from GA.genetic import decoding
from GUI.RunningLine import LineChartView
def Plot(machine_operations,times):
    job_task = [['train%i' % (i + 1), [], []] for i in range(len(machine_operations[0]))]
    plotdata = decoding.translate_decoded_to_plot(machine_operations,job_task)
    res = max([max(i[2]) for i in plotdata])
    charts = LineChartView()
    charts.CreatePlot(len(machine_operations), res, plotdata, 1, str(times))

    # image = charts.grab(QRect(QPoint(0,0),QSize(-1,-1)))
    # image.save(str(times)+'.png')
    return charts
def SortSchedule(machine_operations):
    for i in range(len(machine_operations)):
        machine_operations[i]=sorted(machine_operations[i],key=lambda x:x[3])
        for j in range(len(machine_operations[i])):
            job_index,task_index=machine_operations[i][j][0].split('-')
            machine_operations[i][j][0] = [int(job_index),int(task_index)]
            machine_operations[i][j].append(machine_operations[i][j][1]+machine_operations[i][j][3])
    machine_operations.insert(0,machine_operations[-1])
    machine_operations.pop(len(machine_operations)-1)
    machine_operations.reverse()
    return machine_operations

def SortHelper(machine_operations):
    for i in range(len(machine_operations)):
        machine_operations[i]=sorted(machine_operations[i],key=lambda x:x[3])
    return machine_operations
'''
Args:
    machine_operations:    The schedule of problem

Explanation:
    machine_operation->data:[Task1:[...],           Explanation:Every section schedule on the whole road.
                             Task2:[...],
                             ...........,]
    machine_operation->data->task:[job1:[...],
                                   job2:[...],...]  Explanation:Different train schedule on this section.
    machine_operation->data->task->job:[[job_id,task_id],processTime,LastFinishTime,StartTime]
Return:
    Feasibility of this schedule
'''
def CheckConflict(machine_operations):

    for i in range(len(machine_operations)-1):
        now_task = machine_operations[i]
        next_task = machine_operations[i+1]
        for j in range(len(now_task)):
            for k in range(j+1):
                if now_task[j][3]+now_task[j][1]<next_task[k][3]:
                    job_id = next_task[k][0][0]
                    next_task_machine = -1
                    for m in now_task:
                        if m[0][0]==job_id:
                            next_task_machine=m[4]
                    if job_id != now_task[j][0][0] and now_task[j][4] == next_task_machine:
                        return False
    return True

'''
Args:
    machine_operations:    The schedule of problem
    last_job_index:        Job index in case of conflict
    next_job_index:        Job index affected by conflict
    task_index:            Task index in case of conflict
    
Explanation:
    machine_operation->data:[Task1:[...],           Explanation:Every section schedule on the whole road.
                             Task2:[...],
                             ...........,]
    machine_operation->data->task:[job1:[...],
                                   job2:[...],...]  Explanation:Different train schedule on this section.
    machine_operation->data->task->job:[[job_id,task_id],processTime,LastFinishTime,StartTime]
Return:
    Schedule without conflict (Only repair that task)
'''
def RepairConflictHelper(machine_operations,last_job_index,next_job_index,task_index):
    #出现故障的任务所影响的下一个任务
    next_task = machine_operations[task_index+1]
    #累积时间
    Addtime = next_task[next_job_index][3] - machine_operations[task_index][last_job_index][3] - machine_operations[task_index][last_job_index][1]
    for j in range(last_job_index,len(machine_operations[task_index])):
        if j == next_job_index:
            continue
        #machine_operations[task_index][j][3] += Addtime
        job_id = machine_operations[task_index][j][0][0]
        for i in range(task_index,len(machine_operations)):
            for k in range(len(machine_operations[i])):
                # if k == 0:
                #     last_job_end = 0
                # else:
                #     last_job_end = machine_operations[i][k-1][5]
                if machine_operations[i][k][0][0] == job_id:
                    machine_operations[i][k][3] += Addtime
                    continue
        #Addtime += machine_operations[task_index][j][1]
    return machine_operations
def backward(machine_operations):
    last_finish = {}
    for j in range(len(machine_operations[0])):
        job_id = machine_operations[0][j][0][0]
        if job_id not in last_finish.keys():
            last_finish[job_id]=machine_operations[0][j][5]
        for i in range(1,len(machine_operations)):
            for k in range(len(machine_operations[i])):
                if machine_operations[i][k][0][0]==job_id:
                    machine_operations[i][k][1]=last_finish[job_id]
                    last_finish[job_id]=machine_operations[i][j][1]+machine_operations[i][k][3]
                    machine_operations[i][k][5]=last_finish[job_id]
                    continue
    return machine_operations
'''
Args:
    machine_operations:    The schedule of problem


Explanation:
    machine_operation->data:[Task1:[...],           Explanation:Every section schedule on the whole road.
                             Task2:[...],
                             ...........,]
    machine_operation->data->task:[job1:[...],
                                   job2:[...],...]  Explanation:Different train schedule on this section.
    machine_operation->data->task->job:[[job_id,task_id],processTime,LastFinishTime,StartTime]
Return:
    Schedule without conflict
'''
def RepairConflict(machine_operations):
    counter = 1
    process =[]
    while CheckConflict(machine_operations) != True:
        for i in range(len(machine_operations)-1):
            now_task = machine_operations[i]
            next_task = machine_operations[i+1]
            for j in range(len(now_task)):
                for k in range(j+1):
                    if now_task[j][3] + now_task[j][1] < next_task[k][3]:
                        job_id = next_task[k][0][0]
                        next_task_machine = -1
                        for m in now_task:
                            if m[0][0] == job_id:
                                next_task_machine = m[4]
                        if job_id != now_task[j][0][0] and now_task[j][4] == next_task_machine:
                            machine_operations = SortHelper(RepairConflictHelper(machine_operations,j,k,i))
        #machine_operations=backward(machine_operations)
        process.append(Plot(machine_operations,counter))
        counter += 1
    return machine_operations,process

#!/usr/bin/env python

import sys
from MIP.CalculateByMIP_back import Solve

def split_ms(pb_instance, ms):
    jobs = []
    current = 0
    for index, job in enumerate(pb_instance['jobs']):
        jobs.append(ms[current:current+len(job)])
        current += len(job)
    return jobs


def get_processing_time(op_by_machine, machine_nb):
    for op in op_by_machine:
        if op['machine'] == machine_nb:
            return op['processingTime']
    print("[ERROR] Machine {} doesn't to be able to process this task.".format(machine_nb))
    sys.exit(-1)


def is_free(tab, start, duration):
    for k in range(start, start+duration):
        if not tab[k]:
            return False
    return True


def find_first_available_place(start_ctr, duration, machine_jobs):
    max_duration_list = []
    max_duration = start_ctr + duration

    # max_duration is either the start_ctr + duration or the max(possible starts) + duration
    if machine_jobs:
        for job in machine_jobs:
            max_duration_list.append(job[1]+ job[3])  # start + process time
        max_duration = max(max(max_duration_list), start_ctr) + duration

    machine_used = [True] * max_duration

    # Updating array with used places
    for job in machine_jobs:
        start = job[3]
        long = job[1]
        for k in range(start, start + long):
            machine_used[k] = False

    # Find the first available place that meets constraint
    for k in range(start_ctr, len(machine_used)):
        if is_free(machine_used, k, duration):
            return k

def decode_improve(pb_instance,os,ms):
    ms_s = split_ms(pb_instance, ms)
    pre_jobs=pb_instance['jobs']
    jobs=[]
    for i in range(len(pre_jobs)):
        tasks=[]
        for j in range(len(ms_s[i])):
            tasks.append([pre_jobs[i][j][ms_s[i][j]]])
        jobs.append(tasks)
    pb_instance['jobs']=jobs
    OptimizationResult, job_task, machine_task=Solve(pb_instance)
    return machine_task

def decode(pb_instance, os, ms):
    #decode_improve(pb_instance,os,ms)
    o = pb_instance['jobs']
    machine_operations = [[] for i in range(pb_instance['machinesNb'])]
    ms_s = split_ms(pb_instance, ms)  # machine for each operations
    indexes = [0] * len(ms_s)
    start_task_cstr = [0] * len(ms_s)
    # Iterating over OS to get task execution order and then checking in
    # MS to get the machine
    for job in os:
        index_machine = ms_s[job][indexes[job]]
        machine = o[job][indexes[job]][index_machine]['machine']
        prcTime = o[job][indexes[job]][index_machine]['processingTime']
        start_cstr = start_task_cstr[job]

        # Getting the first available place for the operation
        start = find_first_available_place(start_cstr, prcTime, machine_operations[machine - 1])
        name_task = "{}-{}".format(job, indexes[job]+1)
        '''
            prcTime:Process time of jon on this machine
            start_cstr:The Finish time of this job  on last task
            start:the start time of this job on this task
        '''
        machine_operations[machine - 1].append([name_task, prcTime, start_cstr, start,machine])

        # Updating indexes (one for the current task for each job, one for the start constraint
        # for each job)
        indexes[job] += 1
        start_task_cstr[job] = (start + prcTime)
    return machine_operations

def translate_decoded_to_plot(machine_operations,job_task):
    for idx, machine in enumerate(machine_operations):
        machine_name = "Machine-{}".format(idx + 1)
        operations = []
        for operation in machine:
            operations.append([operation[3], operation[3] + operation[1], operation[0]])
            if len(operation[0])==2:
                job_id=operation[0][0]
                task_id=operation[0][1]
            else:
                job_id,task_id=operation[0].split('-')
                job_id=int(job_id)
                task_id=int(task_id)
            job_task[job_id][2].append(operation[3])
            job_task[job_id][2].append(operation[3] + operation[1])
            job_task[job_id][1].append(task_id - 1)
            job_task[job_id][1].append(task_id)

    for i in job_task:
        i[1]=sorted(i[1],reverse=True)
        i[2]=sorted(i[2])
    return job_task

def translate_decoded_to_gantt(machine_operations):
    data = {}

    for idx, machine in enumerate(machine_operations):
        machine_name = "Machine-{}".format(idx + 1)
        operations = []
        for operation in machine:
            operations.append([operation[3], operation[3] + operation[1], operation[0]])

        data[machine_name] = operations

    return data

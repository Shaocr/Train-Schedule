#!/usr/bin/env python

# This module creates a population of random OS and MS chromosomes

import random
from GA import config


def generateOS(parameters):
    '''
        Args:
            parameters: The data of schedule,contains the number of machine and every task's time cost

        Explanation:

            parameters->data:{MachinesNb:{int}  Explanation:The Number of Machines which are used to work
                                jobs:[...]        Explanation:The data of time cost of jobs on different machines}

            parameters->data->jobs:[job1[...],job2[...],...]
            parameters->data->jobs->job:[task1[...],task2[...],...]
            parameters->data->jobs->job->task:[{machine:{int},processingTime:{int}},...]

        Example:
            parameters={'machinesNb':3,
                            'jobs':[
                                [[{'machine':1,'processingTime':4}],[{'machine':3,'processingTime':4}]],
                                [[{'machine':1,'processingTime':5}],[{'machine':2,'processingTime':4}]]
                            ]}
        Return:
            OS: The order of every job
            Example:
                [2,1,0,0,1,2,2,0,1] can be divided three part
                part1:[2,1,0] means the order of job on task0 is job2 -> job1 -> job0
                part2:[0,1,2] means the order of job on task1 is job0 -> job1 -> job2
                part3:[2,1,0] mean the order of job on task1 is job2 -> job1 -> job0
    '''
    jobs = parameters['jobs']

    OS = []
    i = 0
    for job in jobs:
        for op in job:
            OS.append(i)
        i = i+1

    random.shuffle(OS)

    return OS


def generateMS(parameters):
    jobs = parameters['jobs']

    MS = []
    for job in jobs:
        for op in job:
            randomMachine = random.randint(0, len(op)-1)
            MS.append(randomMachine)

    return MS


def initializePopulation(parameters):
    gen1 = []

    for i in range(config.popSize):
        OS = generateOS(parameters)
        MS = generateMS(parameters)
        gen1.append((OS, MS))

    return gen1

#from import_util import PowDagSim
#from PowDagSim.task import Task
from task import Task
import random

taskDir = "applications"

wkld_base = 10.0

idle_power = 90

def load_task_file(index):

    app_tasks = []
    taskFile = open(taskDir+"/"+str(index), "r")
    #workload = wkld_base + index * random.random()#random.random():0-1之间的随机数
    workload = wkld_base + index * 0.2
    for line in taskFile:
        properties = line.strip().split('\t')
        configIndex = properties[0]
        performance = properties[1]
        power = float(properties[2]) - idle_power
        if float(performance) > 0:
            time = workload / float(performance)
        else:
            time = 0
        tsk = Task(index, configIndex, power, time, performance, workload)
        app_tasks.append(tsk)
    taskFile.close()
    return app_tasks

def load_app_file(index):
    af = open(taskDir+"/"+str(index), "r")
    app_file = af.readlines()
    af.close()
    return app_file

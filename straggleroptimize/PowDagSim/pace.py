#from import_util import PowDagSim
from PowDagSim.task import Task
from PowDagSim.app_file_handler import load_task_file

"""
def get_pace_tasks(toposorted_tasks):
    all_pace_tasks = {}
    pace_sorted_dag = []
    pace_tasks_by_dag_index = {}

    for dictionary in toposorted_tasks:
        group = []
        for index, tasks in dictionary.items():
            app_id = tasks[0].index
            pace_task = get_pace(tasks)
            if app_id not in all_pace_tasks:
                all_pace_tasks[app_id] = pace_task
            if index not in pace_tasks_by_dag_index:
                pace_tasks_by_dag_index[index] = pace_task
            group.append(pace_task)
        pace_sorted_dag.append(group)

    return pace_sorted_dag, all_pace_tasks, pace_tasks_by_dag_index
"""



def get_pace_tasks_of_all_applications(applications, power_cap):
    pace_tasks = [None] * len(applications)

    for index, app in applications.items():
        pace_tasks[index] = get_pace(app.tasks, power_cap)

    return pace_tasks



def get_pace(taskFile, power_cap):
    highestTask = None
    maxVal = -1
    for task in taskFile:
        if power_cap >= task.power > 0:
            ratio = task.speed/(task.power)
        else:
            ratio = 0
        if(ratio >= maxVal):
            maxVal = ratio
            highestTask = task

    maxSpeed = 0
    #if there are multiple configs matching pace, pick the task with higher speed
    for task in taskFile:
        if power_cap >= task.power > 0:
            ratio = task.speed/(task.power)
        else:
            ratio = 0
        if ratio == maxVal:
            if task.speed >= maxSpeed:
                maxSpeed = task.speed
                highestTask = task

    return highestTask



def get_race(taskFile, power_cap):
    highestTask = None
    maxVal = -1
    for task in taskFile:
        if power_cap >= task.power > 0:
            speed = task.speed
        else:
            speed = 0
        if(speed >= maxVal):
            maxVal = speed
            highestTask = task
    curPower = highestTask.power
    #if there are multiple configs matching speed, pick the task with lower power
    for task in taskFile:
        if power_cap >= task.power > 0:
            speed = task.speed
        else:
            speed = 0
        if speed == maxVal:
            if task.power < curPower:
                curPower = task.power
                highestTask = task
    return highestTask







def get_corresponding_tasks_of_all_applications(applications, power_estimate):
    corresponding_tasks = [None] * len(applications)

    for index, app in applications.items():
        for i in range(1,1000):
            corresponding_tasks[index] = min((task for task in app.tasks if power_estimate*(10-i)/10 <= task.power <= power_estimate*(10+i)/10), key = lambda x: x.time, default = None)
            if corresponding_tasks[index] is not None:
                break

    return corresponding_tasks

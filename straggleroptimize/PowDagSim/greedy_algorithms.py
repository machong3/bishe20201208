from PowDagSim.run import Run
from PowDagSim import pace, sim_log
from start import useit

def take_graph_transpose(g):
    """
    USED IN divide_and_conquer.py, DO NOT CHANGE
    g: Directed Acyclic Task Graph in adjacency list format, it is a dictionary of
        (key:value) pairs where value is a set() of neighbors and key is
        an integer index of 0-indexed tasks

    Returns another Directed Acyclic Graph with the same node set but directed
        edges are reversed. Runs in O(# of vertices + # of edges)
    """
    g_t = {}
    for v in g:
        for u in g[v]:
            if u not in g_t:
                g_t[u] = set()
            g_t[u].add(v)
    for u in g:
        if u not in g_t:
            g_t[u] = set()
    return g_t


def get_next_finish(machines_next_finish_t, tasks_on_machines, t):
    """
    USED IN divide_and_conquer.py, DO NOT CHANGE

    machines_next_finish_t : a list:  index it with the machine index
                                it holds the integer time representing the time that
                                the current job on the machine will finishes
    tasks_on_machines : a list indexed with the machine index, holds the task indexed
                        running on that machine. can be None
    t: current time

    Returns next critical time point (acc_min) after t where a machine
            finishes and machine index acc_ind. If two or more machines complete
            at the same time machine completing an actual task (not None)
            is returned -important-.
    """
    acc_min = float('inf')#正无穷
    acc_ind = -1
    for i,v in enumerate(machines_next_finish_t):
        if t <= v < acc_min or (v == acc_min and (tasks_on_machines[acc_ind] is None) and (tasks_on_machines[i] is not None)):
            acc_min = v
            acc_ind = i
    return (acc_min, acc_ind)


def update_time(machines_next_finish_t, tasks_on_machines, t):
    """
    USED IN divide_and_conquer.py, DO NOT CHANGE

    machines_next_finish_t : a list:  index it with the machine index
                                it holds the integer time representing the time that
                                the current job on the machine will finishes
    tasks_on_machines : a list indexed with the machine index, holds the task indexed
                        running on that machine. can be None
    t: current time

    Returns
    """
    acc_min = float('inf')
    acc_ind = -1
    for i,v in enumerate(machines_next_finish_t):
        if t <= v < acc_min and (tasks_on_machines[i] is not None):
            acc_min = v
            acc_ind = i

    for i,v in enumerate(machines_next_finish_t):
        if v < acc_min:
            machines_next_finish_t[i] = acc_min
            tasks_on_machines[i] = None
    return acc_min


def update_ready_nodes(graph_transpose, ready_nodes,  particular_vertex_index = None):
    """
    graph_transpose: Directed Acyclic Task Graph in adjacency list format, it is a dictionary of
                    (key: neighbor set) pairs where neighbor set is a set() and key is
                    an integer index of 0-indexed tasks
    ready_tasks: an (ordered) python-list of integers corresponding to indices
                    of tasks ready to be run.
    particular_vertex_index: an task index appearing in graph_transpose.
                            If specified, only that task is checked to be added to ready_tasks
    """
    if particular_vertex_index:
        if not graph_transpose[particular_vertex_index]:
            ready_nodes.append(particular_vertex_index)
    else: #update every vertex
        for v in graph_transpose:
            if not graph_transpose[v]:
                ready_nodes.append(v)


def set_power_interval(finished_machine_index, power_intervals_of_machines, power_to_be_scheduled):
    int_begin = 0
    for i in range(finished_machine_index-1, -1, -1):
        if power_intervals_of_machines[i] is not None:
            int_begin = power_intervals_of_machines[i][1]
            break
    power_intervals_of_machines[finished_machine_index] = (int_begin, int_begin + power_to_be_scheduled)


def get_next_ready_node_and_config(ready_nodes, node_to_application, rand_wl_scale, applications, running_power, power_cap, lookahead_level, pace_tasks):
    """
    ready_tasks: an (ordered) python-list of integers corresponding to indices
                    of tasks ready to be run.
    tasks_configs: a dictionary with key= integer task index as in task_graph_adj, value= a Task object
    running_power: integer current power, always <= power_cap
    power_cap: integer power cap
    lookahead_level: integer limit on the lookeahead in the ready tasks queue

    Returns the first tasks in the ready tasks list (up to lookahead_level)
            that has power requirement <= power_cap - running_power
    """
    closestNode = None
    closestTaskToPace = None
    closestTaskToPaceDistance = float('Inf')

    for node in ready_nodes[:min(len(ready_nodes), lookahead_level)]:
        pace_task = pace_tasks[node_to_application[node]]
        task = min((x for x in applications[node_to_application[node]].tasks if x.power <= power_cap - running_power and x.configIndex != -1), key=lambda x: (x.time*(rand_wl_scale[node])), default=None)
        if task is not None and abs(pace_task.power - task.power)/pace_task.power < closestTaskToPaceDistance:
            closestNode = node
            closestTaskToPace = task
            closestTaskToPaceDistance = abs(pace_task.power - task.power)/pace_task.power

    if closestTaskToPace is not None:
        return closestNode, closestTaskToPace

    return None, None


def greedy_scheduling(num_machines, number_of_nodes_in_dag, dag_adj_list_by_index, node_to_application, rand_wl_scale, applications, power_cap, lookahead_level):
    """
    num_machines: integer number of parallel machines to schedule the tasks on
    task_graph_adj: Directed Acyclic Task Graph in adjacency list format, it is a dictionary of
                    (key: neighbor set) pairs where neighbor set is a set() and key is
                    an integer index of 0-indexed tasks
    tasks_configs: a dictionary with key= integer task index as in task_graph_adj, value= a Task object
    power_cap: integer power cap
    lookahead_level: integer limit on the lookeahead in the ready tasks queue

    Returns a schedule in the form of a list of PowDagSim.run/Run objects.
    """
    num_nodes = number_of_nodes_in_dag #len(dag_adj_list_by_index)
    runs = []
    ready_nodes = []
    configs_of_nodes = {} #used to keep track of which config is choosen for each node when it is scheduled
    machines_next_finish_t = [0 for i in range(num_machines)] # machine[i] is the next time point machine i will be available
    nodes_on_machines = [None for i in range(num_machines)] # nodes_on_machines[i] the task running on machine i
    power_intervals_of_machines = [None for i in range(num_machines)]
    num_started_nodes = 0
    running_power = 0

    graph_transpose = take_graph_transpose(dag_adj_list_by_index)
    sim_log.log("DEBUG", "Lookahead level: " + str(lookahead_level))
    pace_tasks = pace.get_pace_tasks_of_all_applications(applications, power_cap)
    #print(dag_adj_list_by_index)
    #print(graph_transpose)
    # find ready tasks with 0 incoming edges
    update_ready_nodes(graph_transpose, ready_nodes)




    #initial jobs, each with equal power budget
    initial_power_budget_for_each = power_cap/min(num_machines, len(ready_nodes))
    for i in range(0, min(num_machines, len(ready_nodes))):
        next_ready_node, next_ready_node_task = get_next_ready_node_and_config(ready_nodes, node_to_application, rand_wl_scale, applications, power_cap-initial_power_budget_for_each, power_cap, lookahead_level, pace_tasks)
        sim_log.log("DEBUG", "Next ready nodes: " + str(next_ready_node))
        if next_ready_node is not None:
            configs_of_nodes[next_ready_node] = next_ready_node_task
            machines_next_finish_t[i] = next_ready_node_task.time*(rand_wl_scale[next_ready_node])
            nodes_on_machines[i] = next_ready_node
            set_power_interval(i, power_intervals_of_machines, next_ready_node_task.power)
            running_power += next_ready_node_task.power
            num_started_nodes += 1
            ready_nodes.remove(next_ready_node)
        else:
            break


    t = 0

    while num_started_nodes < num_nodes:

        (finished_time, finished_machine_index) = get_next_finish(machines_next_finish_t, nodes_on_machines, t)
        finished_task = nodes_on_machines[finished_machine_index]
        sim_log.log("DEBUG", "Finished nodes, f time, f machine: " + str(finished_task) + str(finished_time) + str(finished_machine_index))
        if finished_time > t:
            t = finished_time

        if finished_task is not None:
            runs.append(Run(finished_time - configs_of_nodes[finished_task].time*(rand_wl_scale[finished_task]), finished_time, power_intervals_of_machines[finished_machine_index][0], power_intervals_of_machines[finished_machine_index][1], configs_of_nodes[finished_task].power, configs_of_nodes[finished_task].speed, configs_of_nodes[finished_task].workload, configs_of_nodes[finished_task].index, configs_of_nodes[finished_task].configIndex, finished_task))
            running_power -= configs_of_nodes[finished_task].power
            for v in dag_adj_list_by_index[finished_task]:
                graph_transpose[v].remove(finished_task)
                update_ready_nodes(graph_transpose, ready_nodes, v)

        sim_log.log("DEBUG", "Ready nodes: " + str(ready_nodes))
        sim_log.log("DEBUG", "Running power: " + str(running_power))
        sim_log.log("DEBUG", "Next finish times of machines: " + str(machines_next_finish_t))
        sim_log.log("DEBUG", "Indices of nodes on machines: " + str(nodes_on_machines))
        sim_log.log("DEBUG", "Power intervals of machines: " + str(power_intervals_of_machines))

        #there is a next task available to process
        next_ready_node, next_ready_node_task = get_next_ready_node_and_config(ready_nodes, node_to_application, rand_wl_scale, applications, running_power, power_cap, lookahead_level, pace_tasks)
        sim_log.log("DEBUG", "Next ready nodes: " + str(next_ready_node))

        if next_ready_node is not None:
            configs_of_nodes[next_ready_node] = next_ready_node_task
            machines_next_finish_t[finished_machine_index] = max(t, finished_time) + next_ready_node_task.time*(rand_wl_scale[next_ready_node])
            nodes_on_machines[finished_machine_index] = next_ready_node
            set_power_interval(finished_machine_index, power_intervals_of_machines, next_ready_node_task.power)
            running_power += next_ready_node_task.power
            num_started_nodes += 1
            ready_nodes.remove(next_ready_node)


        #ready_nodes are all processed and it is turn for the next level in topo sort
        else:
            if finished_task is not None:
                nodes_on_machines[finished_machine_index] = None
                power_intervals_of_machines[finished_machine_index] = None
            sim_log.log("DEBUG", "Updating t: " + str(t))
            t = update_time(machines_next_finish_t, nodes_on_machines, t)
            sim_log.log("DEBUG", "New t: " + str(t))


    for i,m in enumerate(machines_next_finish_t):
        if m>=t and nodes_on_machines[i] is not None:
            runs.append(Run(m - configs_of_nodes[nodes_on_machines[i]].time*(rand_wl_scale[nodes_on_machines[i]]), m, power_intervals_of_machines[i][0], power_intervals_of_machines[i][1], configs_of_nodes[nodes_on_machines[i]].power, configs_of_nodes[nodes_on_machines[i]].speed, configs_of_nodes[nodes_on_machines[i]].workload, configs_of_nodes[nodes_on_machines[i]].index, configs_of_nodes[nodes_on_machines[i]].configIndex, i))


    return runs


def find_fitting_configurations(configurations, current_level, current_time, node_to_application, rand_wl_scale, applications, pace_tasks, power_cap):
    current_total_power = sum(configurations[job].power for job in current_level)

    while current_total_power > power_cap:
        power_reduce_per_job = (current_total_power - power_cap)/len(current_level)
        for job in current_level:
            candidate_task = min( (task for task in applications[node_to_application[job]].tasks if task.configIndex != -1 and power_reduce_per_job <= configurations[job].power - task.power), key = lambda x: x.power*x.time*(rand_wl_scale[job]) , default=None)
            if candidate_task is not None:
                configurations[job] = candidate_task
        new_current_total_power = sum(configurations[job].power for job in current_level)
        if new_current_total_power < current_total_power:
            current_total_power = new_current_total_power
        else:
            configurations = None
            return


# DONT CHANGE IT, IMPORTED AND USED IN DIVIDE_AND_CONQUER
def select_configuration(taskset,optimizelogs,optimize23,machine_to_task_sep,current_level, current_time, node_to_application, rand_wl_scale, applications, pace_tasks, power_cap):
    print('taskset:',taskset)
    for job in current_level:
        print("job: ", job, "job to app: ", node_to_application[job], "pace task time: ", pace_tasks[node_to_application[job]].time*(rand_wl_scale[job]))

    sim_log.log("DEBUG", "Current level" + str(current_level))

    configurations = {job: pace_tasks[node_to_application[job]] for job in current_level}
    for job in current_level:
        print('初始time  power：',configurations[job].time,configurations[job].power)
    #configurations[job].power是有意义的数量
    #这是一个突破口
    current_total_power = sum(configurations[job].power for job in current_level)
    sim_log.log("DEBUG", "Current level power" + str(current_total_power))


    #this subrotine assumes that the set of jobs given in their pace configurations
    # do not exceed the power_cap and the number of jobs is at most the number of machines

    if current_total_power > power_cap:
        sim_log.log("DEBUG", "Looking for fitting configs")
        find_fitting_configurations(configurations, current_level, current_time, node_to_application, rand_wl_scale, applications, pace_tasks, power_cap)
        if configurations is None:
            return None, None


    #First use all the extra power budget to make the longest jobs shorter
    #Then make shortest jobs longer to make longest jobs shorter

    #take from the extra power budget give to max_time job

    max_time_job = max((job for job in current_level), key = lambda x: configurations[x].time*(rand_wl_scale[x]))
    max_time = configurations[max_time_job].time*(rand_wl_scale[max_time_job])
    max_time_power = configurations[max_time_job].power
    second_max_job = max((job for job in current_level if job != max_time_job), key = lambda x: configurations[x].time*(rand_wl_scale[x]), default=None)
    second_max_time = configurations[second_max_job].time*(rand_wl_scale[second_max_job]) if second_max_job is not None else 0
    candidate_task_of_max = min( (task for task in applications[node_to_application[max_time_job]].tasks if task.configIndex != -1 and task.time*(rand_wl_scale[max_time_job]) < second_max_time), key = lambda x: x.power, default=None)
    #key=power
    while second_max_job is not None and candidate_task_of_max is not None and candidate_task_of_max.power - max_time_power + current_total_power <= power_cap:
        #print("max job: ", max_time_job, "max time: ", max_time, "max app: ", node_to_application[max_time_job], "Candidate max app: ", candidate_task_of_max.configIndex, "candidate max app time: ", candidate_task_of_max.time*(rand_wl_scale[]) )
        #print("sec job: ", second_max_job, "sec time: ", second_max_time, "sec app: ", node_to_application[second_max_job])
        print('candidate_task_of_max.power:', candidate_task_of_max.index,'  ',candidate_task_of_max.power)
        print('max_time_job second_max_job candidate_task_of_max:',max_time_job,' ',second_max_job,' ',candidate_task_of_max)
        configurations[max_time_job] = candidate_task_of_max
        current_total_power = current_total_power + candidate_task_of_max.power - max_time_power
        print('523current_total_power:', current_total_power)
        max_time_job = max((job for job in current_level), key = lambda x: configurations[x].time*(rand_wl_scale[x]))
        max_time = configurations[max_time_job].time*(rand_wl_scale[max_time_job])
        max_time_power = configurations[max_time_job].power
        second_max_job = max((job for job in current_level if job != max_time_job), key = lambda x: configurations[x].time*(rand_wl_scale[x]), default=None)
        second_max_time = configurations[second_max_job].time*(rand_wl_scale[second_max_job]) if second_max_job is not None else 0
        candidate_task_of_max = min( (task for task in applications[node_to_application[max_time_job]].tasks if  task.configIndex != -1 and task.time*(rand_wl_scale[max_time_job]) < second_max_time), key = lambda x: x.power, default=None)
        #key=power
    print('1随时查看：', configurations[job].time, configurations[job].power)#time power没有变
    candidate_task_of_max = min( (task for task in applications[node_to_application[max_time_job]].tasks if task.configIndex != -1 and current_total_power + task.power - max_time_power <= power_cap), key = lambda x: x.time*(rand_wl_scale[max_time_job]), default=None)
    #key=time
    print('node_to_application[max_time_job]:',node_to_application[max_time_job])
    print('1423:',applications[0].idle)
    print(applications[node_to_application[max_time_job]])
    print('applications[node_to_application[max_time_job]].tasks:')
    if candidate_task_of_max is not None:
        print('1.1随时查看：', configurations[job].time, configurations[job].power)
        configurations[max_time_job] = candidate_task_of_max
        print('1.2随时查看：', configurations[job].time, configurations[job].power)
        current_total_power = current_total_power + candidate_task_of_max.power - max_time_power
        max_time = configurations[max_time_job].time*(rand_wl_scale[max_time_job])
        max_time_power = configurations[max_time_job].power
    #end of "take from the extra power budget give to max_time job"
    print('385max_time_job:', max_time_job)
    print('385second_max_job:', second_max_job)#time  power已经变了
    #take from the min_time job give to max_time job
    print('2随时查看：', configurations[job].time, configurations[job].power)
    max_time_job = max((job for job in current_level), key = lambda x: configurations[x].time*(rand_wl_scale[x]))
    max_time = configurations[max_time_job].time*(rand_wl_scale[max_time_job])
    max_time_power = configurations[max_time_job].power
    second_max_job = max((job for job in current_level if job != max_time_job), key = lambda x: configurations[x].time*(rand_wl_scale[x]), default=None)
    second_max_time = configurations[second_max_job].time*(rand_wl_scale[second_max_job]) if second_max_job is not None else 0
    candidate_task_of_max = min( (task for task in applications[node_to_application[max_time_job]].tasks if task.configIndex != -1 and task.time*(rand_wl_scale[max_time_job]) < second_max_time), key = lambda x: x.power, default=None)
    #key为power
    min_time_job = min((job for job in current_level), key = lambda x: configurations[x].time*(rand_wl_scale[x]))
    min_time = configurations[min_time_job].time*(rand_wl_scale[min_time_job])
    min_time_power = configurations[min_time_job].power
    candidate_task_of_min = min( (task for task in applications[node_to_application[min_time_job]].tasks if task.configIndex != -1 and max_time > task.time*(rand_wl_scale[min_time_job]) and task.power < min_time_power), key = lambda x: x.power, default=None)
    #key为power
    print('3随时查看：',configurations[job].time, configurations[job].power)

    while candidate_task_of_min is not None:
        sim_log.log("DEBUG", "max_job, max_time, max_power:" + str(max_time_job) +' \t'+ str(max_time) +' '+ str(max_time_power) )
        sim_log.log("DEBUG", "min_job, min_time, min_power:" + str(min_time_job) +' \t'+ str(min_time) +' '+ str(min_time_power) )
        sim_log.log("DEBUG", "candidate min time, min_power:\t" + str(candidate_task_of_min.time*(rand_wl_scale[min_time_job])) +' '+ str(candidate_task_of_min.power))

        configurations[min_time_job] = candidate_task_of_min
        current_total_power = current_total_power + candidate_task_of_min.power - min_time_power

        max_time_job = max((job for job in current_level), key = lambda x: configurations[x].time*(rand_wl_scale[x]))
        max_time = configurations[max_time_job].time*(rand_wl_scale[max_time_job])
        max_time_power = configurations[max_time_job].power
        candidate_task_of_max = min( (task for task in applications[node_to_application[max_time_job]].tasks if task.configIndex != -1 and task.time*(rand_wl_scale[max_time_job]) < second_max_time), key = lambda x: x.power, default=None)

        while second_max_job is not None and candidate_task_of_max is not None and candidate_task_of_max.power - max_time_power + current_total_power <= power_cap:
            #print("max job: ", max_time_job, "max time: ", max_time, "max app: ", node_to_application[max_time_job], "Candidate max app: ", candidate_task_of_max.configIndex, "candidate max app time: ", candidate_task_of_max.time*(rand_wl_scale[]) )
            #print("sec job: ", second_max_job, "sec time: ", second_max_time, "sec app: ", node_to_application[second_max_job])
            configurations[max_time_job] = candidate_task_of_max
            current_total_power = current_total_power + candidate_task_of_max.power - max_time_power
            max_time_job = max((job for job in current_level), key = lambda x: configurations[x].time*(rand_wl_scale[x]))
            max_time = configurations[max_time_job].time*(rand_wl_scale[max_time_job])
            max_time_power = configurations[max_time_job].power
            second_max_job = max((job for job in current_level if job != max_time_job), key = lambda x: configurations[x].time*(rand_wl_scale[x]), default=None)
            second_max_time = configurations[second_max_job].time*(rand_wl_scale[second_max_job]) if second_max_job is not None else 0
            candidate_task_of_max = min( (task for task in applications[node_to_application[max_time_job]].tasks if  task.configIndex != -1 and task.time*(rand_wl_scale[max_time_job]) < second_max_time), key = lambda x: x.power, default=None)

        candidate_task_of_max = min( (task for task in applications[node_to_application[max_time_job]].tasks if task.configIndex != -1 and current_total_power + task.power - max_time_power <= power_cap), key = lambda x: x.time*(rand_wl_scale[max_time_job]), default=None)
        if candidate_task_of_max is not None:
            configurations[max_time_job] = candidate_task_of_max
            current_total_power = current_total_power + candidate_task_of_max.power - max_time_power
            max_time = configurations[max_time_job].time*(rand_wl_scale[max_time_job])
            max_time_power = configurations[max_time_job].power


        min_time_job = min((job for job in current_level), key = lambda x: configurations[x].time*(rand_wl_scale[x]))
        min_time = configurations[min_time_job].time*(rand_wl_scale[min_time_job])
        min_time_power = configurations[min_time_job].power
        candidate_task_of_min = min( (task for task in applications[node_to_application[min_time_job]].tasks if task.configIndex != -1 and max_time > task.time*(rand_wl_scale[min_time_job]) and task.power < min_time_power), key = lambda x: x.power, default=None)

    #end of "take from the min_time job give to max_time job"

    #prepare the schedule to return
    current_level_schedule = []
    current_power = 0
    print('返回之前的current_level：',current_level)

    #虽然是循环，但是都是同一列之中的任务，最后肯定要先得到每一列执行时间的最大值，可否在外面套一层每一列的大循环？
    #current_level-->current_level1、current_level2、current_level3
    #代码完成！！！需要用复杂的样例来测试
    if(optimize23=="1"):
        everystarttime=current_time
        tasknum=len(current_level)
        print('慢任务优化前的machine_to_task_sep:',machine_to_task_sep)
        dividelist,dividelistpointer=useit(tasknum)#得到一个数组，例如[4],[6]
        optimizelogs.append([])
        optimizelogs[len(optimizelogs) - 1].append(tasknum)
        for i in range(dividelistpointer+1):
            optimizelogs[len(optimizelogs) - 1].append(dividelist[i])
        taskset.append(current_level)
        dividelistbefore=0
        for i in range (dividelistpointer+1):
            machine_change_name=0
            for job in current_level[dividelistbefore:dividelistbefore+dividelist[i]]:
                machine_to_task_sep[job]=machine_change_name
                machine_change_name=machine_change_name+1
                if configurations[job].configIndex == -1:
                    print("CRITICAL", "Found an idle task ", job)
                if (machine_to_task_sep[job] >= 0)and(machine_to_task_sep[job] <= 1):
                    current_level_schedule.append(
                        Run(everystarttime, everystarttime + configurations[job].time * (rand_wl_scale[job]), current_power,
                            current_power + configurations[job].power, configurations[job].power, configurations[job].speed,
                            configurations[job].workload, configurations[job].index, configurations[job].configIndex, job,
                            job))
                if (machine_to_task_sep[job] >= 2)and(machine_to_task_sep[job] <= 2):
                    current_level_schedule.append(
                        Run(everystarttime, everystarttime + configurations[job].time * (rand_wl_scale[job]), current_power,
                            current_power + configurations[job].power, configurations[job].power, configurations[job].speed,
                            configurations[job].workload, configurations[job].index, configurations[job].configIndex, job,
                            job))
                if (machine_to_task_sep[job] >= 3)and(machine_to_task_sep[job] <= 5):
                    current_level_schedule.append(
                        Run(everystarttime, everystarttime + configurations[job].time * (rand_wl_scale[job]) * 6, current_power,
                            current_power + configurations[job].power, configurations[job].power, configurations[job].speed,
                            configurations[job].workload, configurations[job].index, configurations[job].configIndex, job,
                            job))
                current_power = current_power + configurations[job].power
            print('dividelistbefore,dividelistbefore+dividelist[i]:',dividelistbefore,dividelistbefore+dividelist[i])
            everystarttime=max(run.end_time for run in current_level_schedule[dividelistbefore:dividelistbefore+dividelist[i]])
            current_power = 0
            dividelistbefore=dividelistbefore+dividelist[i]
    else:
        taskset.append(current_level)
        for job in current_level:#每次来的job(task)只有一两个
            if configurations[job].configIndex == -1:
                print("CRITICAL", "Found an idle task ", job)
            print(configurations[job].time,configurations[job].power)
            print('257current_time:',current_time)
            #current_level_schedule.append(Run(current_time, current_time + configurations[job].time*(rand_wl_scale[job]),  current_power, current_power + configurations[job].power, configurations[job].power, configurations[job].speed, configurations[job].workload, configurations[job].index, configurations[job].configIndex, job, job))
            #比如这里分三组
            if (machine_to_task_sep[job] >= 0)and(machine_to_task_sep[job] <= 1):
                current_level_schedule.append(
                    Run(current_time, current_time + configurations[job].time * (rand_wl_scale[job]), current_power,
                        current_power + configurations[job].power, configurations[job].power, configurations[job].speed,
                        configurations[job].workload, configurations[job].index, configurations[job].configIndex, job, job))
            if (machine_to_task_sep[job] >= 2)and(machine_to_task_sep[job] <= 2):
                current_level_schedule.append(
                    Run(current_time, current_time + configurations[job].time * (rand_wl_scale[job]), current_power,
                        current_power + configurations[job].power, configurations[job].power, configurations[job].speed,
                        configurations[job].workload, configurations[job].index, configurations[job].configIndex, job, job))
            if (machine_to_task_sep[job] >= 3)and(machine_to_task_sep[job] <= 5):
                current_level_schedule.append(
                    Run(current_time, current_time + configurations[job].time * (rand_wl_scale[job])*6, current_power,
                        current_power + configurations[job].power, configurations[job].power, configurations[job].speed,
                        configurations[job].workload, configurations[job].index, configurations[job].configIndex, job, job))
            current_power = current_power + configurations[job].power

    return current_level_schedule, configurations


def  get_tasks_per_power(taskset,optimizelogs,optimize23,machine_to_task_sep,ready_nodes, node_to_application, rand_wl_scale, applications, pace_tasks, power_cap, z):

    current_power = 0
    count = 0
    for i, node in enumerate(ready_nodes[:z]):
        if current_power + pace_tasks[node_to_application[node]].power > power_cap:
            count = i
            break
        else:
            current_power += pace_tasks[node_to_application[node]].power
            count = i+1

    ignored_schedule, configurations = select_configuration(taskset,optimizelogs,optimize23,machine_to_task_sep,ready_nodes[:count], 0, node_to_application, rand_wl_scale, applications, pace_tasks, power_cap)

    return configurations, count


def naive_grab_all_run_all(taskset,optimizelogs,optimize23,machine_to_task_sep,num_machines, number_of_nodes_in_dag, dag_adj_list_by_index, node_to_application, rand_wl_scale, applications, power_cap):

    runs = []
    #Number of completed tasks
    num_completed_tasks = 0
    #List of all tasks that can be scheduled next (next in task_toposorted)
    graph_transpose = take_graph_transpose(dag_adj_list_by_index)#graph_transpose确实是每一个任务与其父任务的对应关系
    ready_nodes = []
    update_ready_nodes(graph_transpose, ready_nodes)

    pace_tasks = pace.get_pace_tasks_of_all_applications(applications, power_cap)

    t = 0

    while num_completed_tasks < number_of_nodes_in_dag:
        z = min(len(ready_nodes), num_machines)

        if z>0:
            configurations_of_ready_nodes, no_of_current_sched_nodes = get_tasks_per_power(taskset,optimizelogs,optimize23,machine_to_task_sep,ready_nodes, node_to_application, rand_wl_scale, applications, pace_tasks, power_cap, z)
            sim_log.log("DEBUG", "Ready nodes, z, no_of_current_sched_nodes:" + str(ready_nodes) + str(z) + str(no_of_current_sched_nodes) )
        else:
            configurations_of_ready_nodes, no_of_current_sched_nodes = {}, 0
            sim_log.log("DEBUG", "Ready nodes, z, no_of_current_sched_nodes:" + str(ready_nodes) + str(z) + str(no_of_current_sched_nodes) )

        new_ready_nodes = ready_nodes[no_of_current_sched_nodes:]
        current_power = 0
        for node in ready_nodes[:no_of_current_sched_nodes]:
            #画图的一条记录
            runs.append(Run(t, t + configurations_of_ready_nodes[node].time*(rand_wl_scale[node]), current_power, current_power + configurations_of_ready_nodes[node].power, configurations_of_ready_nodes[node].power, configurations_of_ready_nodes[node].speed, configurations_of_ready_nodes[node].workload, configurations_of_ready_nodes[node].index, configurations_of_ready_nodes[node].configIndex, node))
            current_power += configurations_of_ready_nodes[node].power
            for v in dag_adj_list_by_index[node]:
                graph_transpose[v].remove(node)
                update_ready_nodes(graph_transpose, new_ready_nodes, v)
                if not graph_transpose[v]:
                    sim_log.log("DEBUG", "New Ready node :" + str(v))


        t = max((t + task.time*(rand_wl_scale[node]) for node,task in configurations_of_ready_nodes.items()), default=t)
        num_completed_tasks += no_of_current_sched_nodes
        ready_nodes = new_ready_nodes
        sim_log.log("DEBUG", "New Ready nodes, num_completed_tasks:" + str(new_ready_nodes) + str(num_completed_tasks) )

    return runs

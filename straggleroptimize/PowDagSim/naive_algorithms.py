from PowDagSim.run import Run


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
    acc_min = float('inf')
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





def get_next_ready_task(ready_tasks, tasks_configs, running_power, power_cap, lookahead_level):
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
    for task in ready_tasks[:min(len(ready_tasks), lookahead_level)]:
        if (running_power + tasks_configs[task].power <= power_cap):
            return task
    return None






def update_ready_tasks(graph_transpose, ready_tasks,  particular_vertex_index = None):
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
            ready_tasks.append(particular_vertex_index)
    else: #update every vertex
        for v in graph_transpose:
            if not graph_transpose[v]:
                ready_tasks.append(v)



def largest_empty_interval(power_intervals_of_machines, power_cap):
    largest_running_beg = 0
    largest_running_end = 0
    sorted_copy = sorted([x for x in power_intervals_of_machines if x is not None], key=lambda x: x[0])
    for i in range(len(sorted_copy)+1):
        if 0==i<len(sorted_copy) and sorted_copy[0][0] > largest_running_end - largest_running_beg:
            largest_running_beg = 0
            largest_running_end = sorted_copy[0][0]
        if 0<i<len(sorted_copy)-1 and sorted_copy[i][0]-sorted_copy[i-1][1] > largest_running_end - largest_running_beg:
            largest_running_beg = sorted_copy[i-1][1]
            largest_running_end = sorted_copy[i][0]
        if i==len(sorted_copy)>0 and power_cap - sorted_copy[i-1][1] > largest_running_end - largest_running_beg:
            largest_running_beg = sorted_copy[i-1][1]
            largest_running_end = power_cap
    return largest_running_beg, largest_running_end





def naive_scheduling(num_machines, task_graph_adj, tasks_configs, power_cap, lookahead_level):
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
    num_tasks = len(task_graph_adj)
    runs = []
    ready_tasks = []
    machines_next_finish_t = [0 for i in range(num_machines)] # machine[i] is the next time point machine i will be available
    tasks_on_machines = [None for i in range(num_machines)] # tasks_on_machines[i] the task running on machine i
    power_intervals_of_machines = [None for i in range(num_machines)]
    num_started_tasks = 0
    running_power = 0

    graph_transpose = take_graph_transpose(task_graph_adj)
    print("Lookahead level: ", lookahead_level)
    #print(task_graph_adj)
    #print(graph_transpose)
    # find ready tasks with 0 incoming edges
    update_ready_tasks(graph_transpose, ready_tasks)

    t = 0
    while num_started_tasks < num_tasks:
        #input("...")

        (finished_time, finished_machine_index) = get_next_finish(machines_next_finish_t, tasks_on_machines, t)
        finished_task = tasks_on_machines[finished_machine_index]
        print("Finished tasks, f time, f machine: ", finished_task, finished_time, finished_machine_index)
        if finished_time > t:
            t = finished_time

        if finished_task is not None:
            runs.append(Run(finished_time - tasks_configs[finished_task].time, finished_time, power_intervals_of_machines[finished_machine_index][0], power_intervals_of_machines[finished_machine_index][1], tasks_configs[finished_task].power, tasks_configs[finished_task].speed, tasks_configs[finished_task].workload, tasks_configs[finished_task].index, tasks_configs[finished_task].configIndex, finished_task))
            running_power -= tasks_configs[finished_task].power
            for v in task_graph_adj[finished_task]:
                graph_transpose[v].remove(finished_task)
                update_ready_tasks(graph_transpose, ready_tasks, v)

        print("Ready tasks: ", ready_tasks)
        print("Ready times: ",  [tasks_configs[i].time for i in ready_tasks])
        print("Ready powers: ",  [tasks_configs[i].power for i in ready_tasks])
        print("running power: ", running_power)
        print("Next finish times of machines: ", machines_next_finish_t)
        print("Indices of tasks on machines: ", tasks_on_machines)
        print("Power intervals of machines: ", power_intervals_of_machines)

        #there is a next task available to process
        next_ready_task = get_next_ready_task(ready_tasks, tasks_configs, running_power, power_cap, lookahead_level)
        print("Next ready tasks: ", next_ready_task)

        if next_ready_task is not None:
            machines_next_finish_t[finished_machine_index] = max(t, finished_time) + tasks_configs[next_ready_task].time
            tasks_on_machines[finished_machine_index] = next_ready_task
            int_begin, int_finish = largest_empty_interval(power_intervals_of_machines, power_cap)
            power_intervals_of_machines[finished_machine_index] = (int_begin, int_begin + tasks_configs[next_ready_task].power)
            running_power += tasks_configs[next_ready_task].power
            num_started_tasks += 1
            ready_tasks.remove(next_ready_task)


        #ready_tasks are all processed and it is turn for the next level in topo sort
        else:
            if finished_task is not None:
                tasks_on_machines[finished_machine_index] = None
            print("Updating t: ", t)
            t = update_time(machines_next_finish_t, tasks_on_machines, t)
            print("New t: ", t)


    for i,m in enumerate(machines_next_finish_t):
        if m>=t and tasks_on_machines[i] is not None:
            runs.append(Run(m - tasks_configs[tasks_on_machines[i]].time, m, power_intervals_of_machines[i][0], power_intervals_of_machines[i][1], tasks_configs[tasks_on_machines[i]].power, tasks_configs[tasks_on_machines[i]].speed, tasks_configs[tasks_on_machines[i]].workload, tasks_configs[tasks_on_machines[i]].index, tasks_configs[tasks_on_machines[i]].configIndex, i))


    return runs

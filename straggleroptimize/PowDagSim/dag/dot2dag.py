import random
import copy
import networkx as nx
#from toposort import toposort, toposort_flatten

def dot2dag(dot):
    dag = {}
    for line in dot:
        if '{' not in line and '}' not in line:
            line = line.split('\n')[0]
            line = line.split("->")
            if len(line) == 2:
                parent = line[0]
                child = line[1].split()[0]
                parent = parent.strip('\n')
                parent = parent.replace(" ","")
                child = child.strip('\n')
                child = child.replace(" ", "")
                if parent not in dag:
                    dag[parent] = set()
                dag[parent].add(child)

    return dag

def order_dag(dag):
    G = nx.DiGraph()
    for key, val in dag.items():
        G.add_node(key)
        for v in val:
            G.add_edge(key, v)
    #print("Longest path: ", nx.dag_longest_path_length(G))
    return nx.topological_sort(G)

def dag2indeces(dag, ordered):
    orderedlist = list(enumerate(ordered))
    new_dag = []
    for node_set in dag:
        new_node_set = set()
        for node in node_set:
            for element in orderedlist:
                if element[1] == node:
                    new_node_set.add(element[0])
                    break
            #new_node_set.add(next((i for i, item in enumerate(ordered) if item == node), -1))
        new_dag.append(new_node_set)
    return new_dag

def apps2dag_sorted(sorted_dag):
    app_dag = []
    pos = 0
    app_id = 0
    for e in sorted_dag:
        app_dag.append(set())
        num_nodes = len(e)
        for n in range(num_nodes):
            app_id += 1
            app_dag[pos].add(app_id)
        pos += 1
    return app_dag

def dag2list(dag):
    l = []
    num_nodes = 0
    for dag_set in dag:
        list_set = []
        for el in dag_set:
            num_nodes += 1
            list_set.append(el)
        list_set.sort()
        l.append(list_set)
    l.sort(key=lambda x: x[0])
    return l, num_nodes

def dag2allTasks(dag, applications, num_apps, app_file = 0, app_out_file = 0):
    app_out = 0
    app_in = 0
    wkld_base = 50
    assignment_dict = {}
    workload = 0
    app_id = -1
    if app_out_file != 0:
        app_out = open(app_out_file, 'w')
    if app_file != 0:
        app_in = open(app_file, 'r')
        for line in app_in.readlines():
            els = line.split('\t')
            index = els[0]
            app_index = els[1]
            wkld = els[2]
            assignment_dict[int(index)] = [int(app_index), float(wkld)]
        app_in.close()
    task_graph = []
    for group in dag:
        task_group_d = {}
        for index in group:
            if app_file != 0:
                app_id = assignment_dict[index][0]
                workload = assignment_dict[index][1]
            else:
                app_id = random.randint(0, num_apps - 1)
                workload = wkld_base + index * random.random()

                if app_out_file != 0:
                    app_out.write(str(index) + "\t"+ str(app_id) +"\t"+str(workload)+"\r")
            tasks = copy.deepcopy(applications[app_id].tasks)
            for task in tasks:
                task.dag_index = index
                task.workload = workload
            task_group_d[index] = tasks
        task_graph.append(task_group_d)
    return task_graph



def find_inv(a,m):
    r = 1
    found = 0
    while found < 15:
        r += m
        if r % a == 0:
            print(r/a)
            found += 1
    found = 0
    r = 1
    while found < 15:
        r -= m
        if r % a == 0:
            print(r/a)
            found += 1


def add_dag_indeces(task_graph, app_file = 0):
    wkld_base = 50
    for dictionary in task_graph:
        for dag_index, tasks in dictionary.items():
            if app_file != 0:
                #read from app file
                app_file = 0 #CHANGE
            else:
                workload = wkld_base + dag_index * random.random()
            for task in tasks:
                task.dag_index = dag_index
                task.workload = workload
    return task_graph


"""
def setup_dag(dag_file_path, applications, num_apps, app_indir = 0):
    '''TODO: add file exception handling'''
    '''TODO: test reading application index assignment from file'''
    dot_dag_file = open(dag_file_path,"r")
    dot_dag = dot2dag(dot_dag_file)
    dot_dag_file.close()

    toposort_ordering = order_dag(dot_dag)
    dot_toposorted = list(toposort(dot_dag))
    task_graph_by_index = dag2indeces(dot_toposorted, toposort_ordering)
    (task_graph_by_index, num_dag_nodes) = dag2list(task_graph_by_index)

    if app_indir != 0:
        app_file = open(app_indir, 'r')
    else:
        app_file = 0

    task_graph = dag2allTasks(task_graph_by_index, applications, num_apps, app_file)
    #task_graph = add_dag_indeces(task_graph, app_file)

    return task_graph, num_dag_nodes
"""

def print_dag_info(dag):
    return 0

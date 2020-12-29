import random
import copy
import networkx as nx
import os.path

num_apps = 26

def swift2dag(dot):
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

'''This is buggy'''
def cfg2dag(directory):
    dag = {}
    dirs = os.listdir(directory)
    dots = []
    for file in dirs:
        if file != 'callgraph.dot':
            c = file.split('.')
            if c[len(c) - 1] == 'dot':
                dots.append(c[1])
            
    callgraph = open(directory+"/callgraph.dot", 'r')
    node_label = {}
    for line in callgraph:
        line = line.split('\n')[0]
        l = line.split()
        if len(l) == 2:
            if '[' in l[1]:
                ll = l[1].split(',')[1]
                ll = ll.split('=')
                if ll[0] == 'label':
                    label = ll[1].split('{')[1]
                    label = label.split('}')[0]
                    node = l[0]
                    node = node.strip()
                    node = node.strip('\t')
                    if node not in node_label:
                        node_label[node] = label
        line = line.split("->")
        if len(line) == 2:
            parent = line[0]
            child = line[1].split()[0]
            parent = parent.strip('\n')
            parent = parent.strip('\t')
            parent = parent.replace(" ","")
            parent = parent.split(':')[0]
            child = child.strip('\n')
            child = child.strip(';')
            child = child.replace(" ", "")
            if parent not in dag:
                dag[parent] = set()
            dag[parent].add(child) 
            if child in node_label:
                if node_label[child] in dots:
                    num_nodes = 0
                    dot = open(directory+"/"+"cfg."+node_label[child]+".dot", 'r')
                    for dot_line in dot:
                        if '{' not in line and '}' not in line:
                            dot_line = dot_line.split('\n')[0]
                            dot_line = dot_line.split("->")
                            if len(dot_line) == 2:
                                dot_parent = dot_line[0]
                                dot_child = dot_line[1].split()[0]
                                dot_child = dot_child.strip(';')
                                dot_child = node_label[child]+"-"+dot_child
                                dot_parent = dot_parent.strip('\n')
                                dot_parent = dot_parent.replace(" ","")
                                dot_parent = dot_parent.split(':')[0]
                                dot_parent = dot_parent.strip('\t')
                                dot_parent = node_label[child]+"-"+dot_parent #to guarentee uniqunes
                                if num_nodes == 0:
                                    if child not in dag:
                                        dag[child] = set()
                                    dag[child].add(dot_parent)
                                dot_child = dot_child.strip('\n')
                                dot_child = dot_child.replace(" ", "")
                                if dot_parent not in dag:
                                    dag[dot_parent] = set()
                                dag[dot_parent].add(dot_child)
                                num_nodes += 1
                    dot.close()
                    dots.remove(node_label[child])
                           
    if len(dots) > 0:
        print("WARNING, not all subfunctions have been processed from callgraph")
    callgraph.close()
    
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
    new_dag = []
    for node_set in dag:
        new_node_set = set()
        for node in node_set:
            new_node_set.add(ordered.index(node))
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

def dag2allTasks(dag, applications):
    task_graph = []
    for group in dag:
        task_group_d = {}
        for index in group:
            app_id = random.randint(0, num_apps - 1)
            task_group_d[index] = copy.deepcopy(applications[app_id].tasks)
        task_graph.append(task_group_d)
    return task_graph

def add_dag_indeces(task_graph):
    wkld_base = 50
    for dictionary in task_graph:
        for dag_index, tasks in dictionary.items():
            workload = wkld_base + dag_index * random.random()
            for task in tasks:
                task.dag_index = dag_index
                task.workload = workload
    return task_graph
#{'21': {'f1_argwait_0_215'}, 
 #'26': {'f2_argwait_0_216'}, 
 #'25': {'f1_argwait_0_216'}, 
 #'9': {'f1_argwait_0_214'}, 
 #'5': {'__entry_wait_range1_0_212'}, 
 #'f2_0_218': {'44', '45', '40', '41'}, 
 #'7': {'__entry_wait_range1_0_212'}, 
 #'41': {'f1_argwait_0_218'}, 
 #'f2_0_215': {'21', '17', '20', '16'}, 
 #'f2_0_219': {'38', '10', '26', '47', '42', '22', '46', '18', '11', '43', '35', '19', '15', '39', '30', '14', '27', '31', '34', '23'}, 
 #'4': {'copy___t_4_NODE_0_212'}, 
 #'29': {'f1_argwait_0_216'}, 
 #'6': {'__entry_wait_range1_0_212'}, 
 #'f2_0_216': {'25', '28', '24', '29'}, 
 #'45': {'f1_argwait_0_219'}, 
 #'38': {'f2_argwait_0_218'}, 
 #'34': {'f2_argwait_0_217'}, 
 #'3': {'copy___t_3_RANK_0_212'}, 
 #'13': {'f1_argwait_0_214'}, 
 #'f2_0_214': {'13', '12'}, 
 #'42': {'f2_argwait_0_218'}, 
 #'30': {'f2_argwait_0_217'}, 
 #'2': {'copy___t_2_SOFT_0_211'}, 
 #'18': {'f2_argwait_0_215'}, 
 #'17': {'f1_argwait_0_215'}, 
 #'46': {'f2_argwait_0_219'}, 
 #'33': {'f1_argwait_0_217'}, 
 #'1': {'copy___t_1_HARD_0_211'}, 
 #'22': {'f2_argwait_0_216'}, 
 #'10': {'f2_argwait_0_214'}, 
 #'37': {'f1_argwait_0_218'}, 
 #'__entry_0_134': {'3', '9', '2', '5', '7', '4', '8', '6', '1'}, 
 #'f2_0_217': {'36', '32', '37', '33'}, 
 #'14': {'f2_argwait_0_215'}}

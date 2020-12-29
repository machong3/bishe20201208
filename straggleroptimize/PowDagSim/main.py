import os
import argparse
import sys
import random
import time
import copy


import import_util
from PowDagSim import application, job, sim_log, dag, pace, task, divide_and_conquer, greedy_algorithms, plot#, scheduler

parser = argparse.ArgumentParser()
parser.add_argument('-m','--num-machines', help='Number of machines in the system', default=5, required=False, type=int)
parser.add_argument('-P','--power-cap', help='Global power cap (W)', default=200, required=False, type=int)
parser.add_argument('-a', '--num-apps', help='Number of applications to use to map to DAG', default=15, required=False, type=int)
parser.add_argument('-L', '--debug-level', help='Debug level [CRITICAL, ERROR, WARNING, INFO, DEBUG, TRACE]', default="TRACE", required=False)
parser.add_argument('-d', '--dag', help='Name of .dot file containing DAG structure', default="kmeans", required=False)
parser.add_argument('-A', '--algorithm', nargs='+', help='Algorithm to use [NAIVE, DIVIDECONQUER]', default="NAIVE", required=False)
parser.add_argument('-l', '--lookahead', help='Look Ahead Level for the naive algorithm: an integer from 1 to 100000', default=1, required=False, type=int, choices=range(1,100001))
parser.add_argument('-s', '--simulation-count', help='How many times to simulate: an integer', default=1, required=False, type=int, choices=range(1,200))
parser.add_argument('-op', '--optimize23',default="1")
args = parser.parse_args()

optimize23=args.optimize23
num_machines = args.num_machines
power_cap = args.power_cap
num_apps = args.num_apps
dag_name = args.dag
lookahead_level = args.lookahead
simulation_count = args.simulation_count#default=10
#赋值

sim_log.loglevel = args.debug_level

NAIVE = True
DIVIDECONQUER = True


if "NAIVE" in args.algorithm:
    NAIVE = True
if "DIVIDECONQUER" in args.algorithm:
    DIVIDECONQUER = True







print('num_apps, power_cap:',num_apps, power_cap)
sim_log.log("INFO", "Initializing all applications...")
applications = application.init_all_apps(num_apps, power_cap)

sim_log.log("INFO", "Getting dot dag...")#得到点DAG
print('得到点DAG步骤里面DAG_name为：',dag_name)
dot_dag_file = open(os.path.join("dag",dag_name+".dot"),"r")
dot_dag = dag.dot2dag.dot2dag(dot_dag_file)
dot_dag_file.close()
print('dot_dag_file内容为：',dot_dag_file)
print('dot_dag内容为：',dot_dag)
#read here 2020/9/3
sim_log.log("DEBUG", "dot_dag: ", list(dot_dag.items()))

toposort_ordering = list(dag.dot2dag.order_dag(dot_dag))
sim_log.log("DEBUG", "toposort_ordering: ", toposort_ordering)
print('toposort_ordering内容为：',toposort_ordering)
print('toposort_ordering)内容为：',toposort_ordering)
name_to_index = {}
for index, name in list(enumerate(toposort_ordering)):
        name_to_index[name] = index
print('name_to_index内容为',name_to_index)
dag_adj_list_by_index = {}
for index, name in list(enumerate(toposort_ordering)):#toposort_ordering的数据交给dag_adj_list_by_index
    dag_adj_list_by_index[index] = set([name_to_index[x] for x in dot_dag[name]]) if name in dot_dag else set([])

#dag_adj_list_by_index={0: {25}, 1: {25}, 2: {25}, 3: {25}, 4: {25}, 5: {25}, 6: {25}, 7: {25}, 8: {25}, 9: {25}, 10: {25}, 11: {25}, 12: {25}, 13: {25}, 14: {25}, 15: {25}, 16: {25}, 17: {32, 34, 35, 36, 37, 38, 39, 41, 44, 46, 50, 52, 53, 54, 55, 56, 25, 59, 28}, 18: {25}, 19: {25}, 20: {36, 39}, 21: {25}, 22: {33, 34, 35, 48, 54, 57}, 23: {25}, 24: {25}, 25: set(), 26: {49, 35, 54, 47}, 27: {28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59}, 28: set(), 29: set(), 30: set(), 31: set(), 32: set(), 33: set(), 34: set(), 35: set(), 36: set(), 37: set(), 38: set(), 39: set(), 40: set(), 41: set(), 42: set(), 43: set(), 44: set(), 45: set(), 46: set(), 47: set(), 48: set(), 49: set(), 50: set(), 51: set(), 52: set(), 53: set(), 54: set(), 55: set(), 56: set(), 57: set(), 58: set(), 59: set()}
#print('1426dag_adj_list_by_index:',dag_adj_list_by_index.values())
#with open('dag_adj_list_by_index.txt','w') as f:
    #f.write(str(dag_adj_list_by_index))
with open('dag_adj_list_by_index_'+dag_name+'.txt', 'r') as f:
    dag_adj_list_by_index2=f.read()
dag_adj_list_by_index=eval(dag_adj_list_by_index2)

number_of_nodes_in_dag = len(toposort_ordering)

sim_log.log("INFO", "Number of Nodes: ", [number_of_nodes_in_dag])
sim_log.log("DEBUG", "This is adj list by index: ", list(dag_adj_list_by_index.items()))
#print('1425dag_adj_list_by_index:',dag_adj_list_by_index)
print('各任务DAG图：',dag_adj_list_by_index)

with open('DAGpicture.txt','w') as f:
    f.write("DAG图——任务之间的依赖关系：\n")
    for i in range(len(dag_adj_list_by_index)):
        f.write("{"+str(i)+"}-->"+str(dag_adj_list_by_index[i])+"\n")
sim_log.log("DEBUG", "This is the ordering of the DAG nodes:\n\t", toposort_ordering)

optimizelogs=[ ([]) for i in range(0)]
taskset=[]


simulation_stats = [0, 0, 0, 0, 0]

simulation_results_exectime = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
simulation_results_makespan = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
simulation_results_energy = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
simulation_results_makespan_percent = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
simulation_results_energy_percent = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

for simulation_count_current in range(simulation_count):

    sim_log.log("INFO", "Extending the application with random perturbation(扰动) from the original(原始的) applications...")
    rand_wl_scale = [1] * number_of_nodes_in_dag
    rand_scale_mean = 2
    rand_scale_var = 0.5
    for i in range(number_of_nodes_in_dag):
        rand_workload_scale = random.gauss(rand_scale_mean, rand_scale_var)
        while rand_workload_scale <= 0 or rand_workload_scale >= 2*rand_scale_mean:
            rand_workload_scale = random.gauss(rand_scale_mean, rand_scale_var)
        rand_wl_scale[i] = rand_workload_scale

    #rand_wl_scale=[2.309094659923832, 1.6637374899560309, 0.6790113354355898, 2.669796526612871, 1.1270080077843727, 1.9123113042161648, 3.0068079237528047, 2.0331185867188526, 1.5291644703719705, 1.6873187177169127, 1.7066163343186846, 2.6193665162602024, 1.5785872658197848, 1.9075639194943417, 2.028646285931144, 2.6476542356264674, 2.3437787646444743, 0.9820255231286155, 1.0360160526572544, 1.9509688487284589, 2.951396147121732, 2.628875233890779, 1.4687156686863472, 2.1067549995125368, 1.8613189123703242, 0.7640436193831781, 1.4573963092705928, 1.2036488433688453, 2.1438562151592073, 1.359404704293564, 2.1911024031285566, 1.3000196382122213, 1.405324719109243, 2.71186724595831, 1.6971361372398797, 1.4837126293983145, 1.7721757935236058, 2.613276369678887, 2.1085130876817306, 1.9912282081736083, 2.574287002627489, 2.0915372866370974, 2.3598832827990894, 2.341718047961595, 1.6188513758696892, 1.0424962774690696, 1.8471410487442332, 2.891527574670995, 2.8246224784689398, 1.245659825057379, 2.044204032218977, 1.4777099048400526, 2.3745468447948106, 1.9698149063323882, 2.6097613045993913, 1.7525855925421963, 1.7335986920749276, 2.233374131479658, 1.2175737515273264, 1.8268666425888096]
    print('1425rand_wl_scale:',rand_wl_scale)
    #with open('rand_wl_scale.txt', 'w') as f:
        #f.write(str(rand_wl_scale))
    with open('rand_wl_scale_'+dag_name+'.txt', 'r') as f:
        rand_wl_scale = eval(f.read())
        #extended_applications[i] = application.Application(i)
        #extended_applications[i].tasks = copy.deepcopy(applications[random.randint(0, num_apps - 1)].tasks)
        #for task in extended_applications[i].tasks:
        #    task.workload = task.workload * rand_workload_scale
        #    if float(task.speed) > 0:
        #        task.time = task.workload / float(task.speed)
        #    else:
        #        task.time = 0

    sim_log.log("INFO", "Assigning applications to dag nodes...")
    node_to_application = [0] * number_of_nodes_in_dag#15
    for i in range(number_of_nodes_in_dag):
#        node_to_application[i] = i
        node_to_application[i] = random.randint(0, num_apps - 1)
        print('node_to_application[',i,']:',node_to_application[i])
    #node_to_application=[14, 13, 13, 5, 6, 12, 9, 14, 11, 3, 12, 2, 9, 7, 8, 4, 6, 10, 11, 14, 14, 9, 5, 13, 6, 14, 13, 6, 8, 4, 6, 10, 1, 3, 11, 13, 6, 0, 12, 5, 8, 3, 14, 1, 7, 2, 7, 6, 10, 7, 7, 4, 5, 2, 0, 10, 13, 1, 5, 1]
    print('1425node_to_application:',node_to_application)
    #with open('node_to_application.txt', 'w') as f:
        #f.write(str(node_to_application))
    #with open('node_to_application_'+dag_name+'.txt', 'r') as f:
    with open('node_to_application_'+dag_name+'.txt', 'r') as f:
        node_to_application = eval(f.read())
    print(list(enumerate(node_to_application)))
    sim_log.log("DEBUG", "===========")
    for node_index, app_index in enumerate(node_to_application):
        sim_log.log("DEBUG", "...")


        sim_log.log("DEBUG", "\t\tapp_index: ", printlist=[app_index, ", dag_index: ", node_index])
    sim_log.log("DEBUG", "===========")##输出15个

    sim_log.log("DEBUG", "Pace Tasks ===========")
    pace_tasks = pace.get_pace_tasks_of_all_applications(applications, power_cap)
    for app_index, task in enumerate(pace_tasks):
        sim_log.log("DEBUG", "...")
        sim_log.log("DEBUG", "\tapp_index: ", printlist=[app_index, " \tconfigIndex: ", task.configIndex, " time: ", task.time, " speed: ", task.speed, " power: ", task.power, " workload: ", task.workload])
    sim_log.log("DEBUG", "Pace Tasks ===========")

#    sim_log.log("INFO", "Corresponding Tasks ===========")
#    corresponding_tasks = pace.get_corresponding_tasks_of_all_applications(applications, power_cap/num_machines)
#    for app_index, task in enumerate(corresponding_tasks):
#        sim_log.log("INFO", "...")
#        sim_log.log("INFO", "\tapp_index: ", printlist=[app_index, " \tconfigIndex: ", task.configIndex, " time: ", task.time, " speed: ", task.speed, " power: ", task.power, " workload: ", task.workload])
#    sim_log.log("INFO", "Corresponding Tasks ===========")
    print('number_of_nodes_in_dag:',number_of_nodes_in_dag)
    dummy_diff = sum(pace_tasks[node_to_application[i]].power for i in range(number_of_nodes_in_dag))/number_of_nodes_in_dag
    simulation_stats[0] += dummy_diff
    sim_log.log("INFO", "Mean Pace Tasks Power:" + str(dummy_diff))

    dummy_diff = sum(pace_tasks[node_to_application[i]].power*pace_tasks[node_to_application[i]].time*rand_wl_scale[i] for i in range(number_of_nodes_in_dag))/sum(pace_tasks[node_to_application[i]].time*rand_wl_scale[i] for i in range(number_of_nodes_in_dag))
    simulation_stats[1] += dummy_diff
    sim_log.log("INFO", "Time Weighted Mean Pace Tasks Power:" + str(dummy_diff))

    dummy_diff = sorted(pace_tasks, key=lambda x: x.power)[int(len(pace_tasks)/2 +1)].power
    simulation_stats[2] += dummy_diff
    sim_log.log("INFO", "Median Pace Tasks Power:" + str(dummy_diff))

    dummy_diff = sum(pace_tasks[node_to_application[i]].time*rand_wl_scale[i] for i in range(number_of_nodes_in_dag))/number_of_nodes_in_dag
    simulation_stats[3] += dummy_diff
    sim_log.log("INFO", "Mean Pace Tasks Time:" + str(dummy_diff))

    dummy_diff = (sorted(pace_tasks, key=lambda x: x.time)[int(len(pace_tasks)/2 +1)].time )*rand_scale_mean
    simulation_stats[4] += dummy_diff
    sim_log.log("INFO", "Median Pace Tasks Time:" + str(dummy_diff))
    #[ INFO ] Mean Pace Tasks Power:23.158333333333328
    #[ INFO ] Time Weighted Mean Pace Tasks Power:29.259969449997232
    #[ INFO ] Median Pace Tasks Power:31.099999999999994
    #[ INFO ] Mean Pace Tasks Time:53.08581563964435
    #[ INFO ] Median Pace Tasks Time:8.18651178697667

    #sim_log.log("INFO", "Assigning power cap based on", printlist=[len(all_pace_tasks), "tasks..."])
    sim_log.log("INFO", "Power cap: " + str(power_cap) + " W")
    sim_log.log("INFO", "Number of DAG nodes:"+ str(number_of_nodes_in_dag))
    sim_log.log("INFO", "Simulation iteration: "+ str(simulation_count_current) + " out of "+ str(simulation_count))


    runs = []
    runs_op = []
    runs_dc = []
    runs_greedy = []
    runs_naive = []
    machine_to_task_sep=[0]*number_of_nodes_in_dag



    #if NAIVE:

    #if DIVIDECONQUER:

    outDir = "output"

    def runs2file(runs, fileName):
        outfile = open(os.path.join(outDir,fileName), "w")
        tab = "\t"
        nl = "\n"
        for run in runs:
            if run.config_index == -1:
                sim_log.log("CRITICAL", "Found an idle task in run file " + fileName + ", which is not supposed to happen.")
                #outFile.close()
                outfile.close()
                sys.exit(1)
            line = str(run.start_time) + tab + str(run.end_time) + tab + str(run.power_start) + tab + str(run.power_end) + tab + str(run.power) + tab + str(run.speed) + tab + str(run.workload) + tab + str(run.app_id) + tab + str(run.config_index) + tab + str(run.dag_index) + nl
            outfile.write(line)
        outfile.close()

    #Theoretical possible
    sim_log.log("INFO", "Finish time and total energy, possible Optimal: \t\t\t" + str(int(sum(pace_tasks[node_to_application[job]].power*pace_tasks[node_to_application[job]].time*(rand_wl_scale[job]) for job in range(number_of_nodes_in_dag))/power_cap)) + ' \t' + str(int(sum(pace_tasks[node_to_application[job]].power*pace_tasks[node_to_application[job]].time*(rand_wl_scale[job]) for job in range(number_of_nodes_in_dag)))) )
    simulation_results_makespan[8] += sum(pace_tasks[node_to_application[job]].power*pace_tasks[node_to_application[job]].time*(rand_wl_scale[job]) for job in range(number_of_nodes_in_dag))/power_cap
    simulation_results_energy[8]  += sum(pace_tasks[node_to_application[job]].power*pace_tasks[node_to_application[job]].time*(rand_wl_scale[job]) for job in range(number_of_nodes_in_dag))
    simulation_results_makespan_last_sim = sum(pace_tasks[node_to_application[job]].power*pace_tasks[node_to_application[job]].time*(rand_wl_scale[job]) for job in range(number_of_nodes_in_dag))/power_cap
    simulation_results_energy_last_sim  = sum(pace_tasks[node_to_application[job]].power*pace_tasks[node_to_application[job]].time*(rand_wl_scale[job]) for job in range(number_of_nodes_in_dag))
    print('program comes here~203')
    idle_pow = 90

    if NAIVE:#程序确实进入了NAIVE


        time1 = time.clock()
        print('program comes here~210')
        runs_naive = greedy_algorithms.naive_grab_all_run_all(taskset,optimizelogs,optimize23,machine_to_task_sep,num_machines, number_of_nodes_in_dag, dag_adj_list_by_index, node_to_application, rand_wl_scale, applications, power_cap)
        print('program comes here~211')
        print('runs_naive的内容：',runs_naive)
        time2 = time.clock()
        runs_naive.sort(key=lambda x: x.end_time)
        #runs2file(runs_naive, "naive-greedy-" +dag_name+".txt")
        idle_energy_naive = runs_naive[-1].end_time * idle_pow * num_machines
        runtime_energy_naive = sum(run.power*(run.end_time - run.start_time) for run in runs_naive)
        sim_log.log("INFO", "Finish time and total power, time of naive : \t\t\t\t" + str(int(runs_naive[-1].end_time)) + ' \t' + str(int(idle_energy_naive + runtime_energy_naive))+' = '+str(int(idle_energy_naive)) +  ' + ' + str(int(runtime_energy_naive)) + ' \t\t' + str((time2-time1)))
        #plot.draw_pow_opt("naive-greedy-"+dag_name, ".txt", power_cap, True, False)
        simulation_results_makespan[9] += runs_naive[-1].end_time
        simulation_results_energy[9] += runtime_energy_naive
        simulation_results_makespan_percent[9] += 100*((runs_naive[-1].end_time - simulation_results_makespan_last_sim)/simulation_results_makespan_last_sim)
        simulation_results_energy_percent[9] += 100*((runtime_energy_naive-simulation_results_energy_last_sim)/simulation_results_energy_last_sim)
        simulation_results_exectime[9] += time2-time1

        time1 = time.clock()
        runs_greedy = greedy_algorithms.greedy_scheduling(num_machines, number_of_nodes_in_dag, dag_adj_list_by_index, node_to_application, rand_wl_scale, applications, power_cap, 1)
        time2 = time.clock()
        runs_greedy.sort(key=lambda x: x.end_time)
        #runs2file(runs_greedy, "greedy-20201111-level-1" + "-" +dag_name+".txt")
        idle_energy_greedy = runs_greedy[-1].end_time * idle_pow * num_machines
        runtime_energy_greedy = sum(run.power*(run.end_time - run.start_time) for run in runs_greedy)
        sim_log.log("INFO", "Finish time and total power, time of greedy lookahead " + str(1) + ' : \t\t' + str(int(runs_greedy[-1].end_time)) + ' \t' + str(int(idle_energy_greedy + runtime_energy_greedy))+' = '+str(int(idle_energy_greedy)) + ' + '+str(int(runtime_energy_greedy)) + ' \t\t' + str((time2-time1)))
        #plot.draw_pow_opt("greedy-20201111-level-1" + "-"+dag_name, ".txt", power_cap, True, False)
        simulation_results_makespan[0] += runs_greedy[-1].end_time
        simulation_results_energy[0] += runtime_energy_greedy
        simulation_results_makespan_percent[0] += 100*((runs_greedy[-1].end_time - simulation_results_makespan_last_sim)/simulation_results_makespan_last_sim)
        simulation_results_energy_percent[0] += 100*((runtime_energy_greedy-simulation_results_energy_last_sim)/simulation_results_energy_last_sim)
        simulation_results_exectime[0] += time2-time1

        time1 = time.clock()
        runs_greedy = greedy_algorithms.greedy_scheduling(num_machines, number_of_nodes_in_dag, dag_adj_list_by_index, node_to_application, rand_wl_scale, applications, power_cap, 10)
        time2 = time.clock()
        runs_greedy.sort(key=lambda x: x.end_time)
        #runs2file(runs_greedy, "greedy-level-" +lookahead_str+"-" +dag_name+".txt")
        idle_energy_greedy = runs_greedy[-1].end_time * idle_pow * num_machines
        runtime_energy_greedy = sum(run.power*(run.end_time - run.start_time) for run in runs_greedy)
        sim_log.log("INFO", "Finish time and total power, time of greedy lookahead " + str(10) + ' : \t\t' + str(int(runs_greedy[-1].end_time)) + ' \t' + str(int(idle_energy_greedy + runtime_energy_greedy))+' = '+str(int(idle_energy_greedy)) + ' + '+str(int(runtime_energy_greedy)) + ' \t\t' + str((time2-time1)))
        #plot.draw_pow_opt("greedy-level-" +lookahead_str+"-"+dag_name, ".txt", power_cap, True, False)
        simulation_results_makespan[1] += runs_greedy[-1].end_time
        simulation_results_energy[1] += runtime_energy_greedy
        simulation_results_makespan_percent[1] += 100*((runs_greedy[-1].end_time - simulation_results_makespan_last_sim)/simulation_results_makespan_last_sim)
        simulation_results_energy_percent[1] += 100*((runtime_energy_greedy-simulation_results_energy_last_sim)/simulation_results_energy_last_sim)
        simulation_results_exectime[1] += time2-time1


        time1 = time.clock()
        runs_greedy = greedy_algorithms.greedy_scheduling(num_machines, number_of_nodes_in_dag, dag_adj_list_by_index, node_to_application, rand_wl_scale, applications, power_cap, 20)
        time2 = time.clock()
        runs_greedy.sort(key=lambda x: x.end_time)
        #runs2file(runs_greedy, "greedy-level-" +lookahead_str+"-" +dag_name+".txt")
        idle_energy_greedy = runs_greedy[-1].end_time * idle_pow * num_machines
        runtime_energy_greedy = sum(run.power*(run.end_time - run.start_time) for run in runs_greedy)
        sim_log.log("INFO", "Finish time and total power, time of greedy lookahead " + str(20) + ' : \t\t' + str(int(runs_greedy[-1].end_time)) + ' \t' + str(int(idle_energy_greedy + runtime_energy_greedy))+' = '+str(int(idle_energy_greedy)) + ' + '+str(int(runtime_energy_greedy)) + ' \t\t' + str((time2-time1)))
        #plot.draw_pow_opt("greedy-level-" +lookahead_str+"-"+dag_name, ".txt", power_cap, True, False)
        simulation_results_makespan[2] += runs_greedy[-1].end_time
        simulation_results_energy[2] += runtime_energy_greedy
        simulation_results_makespan_percent[2] += 100*((runs_greedy[-1].end_time - simulation_results_makespan_last_sim)/simulation_results_makespan_last_sim)
        simulation_results_energy_percent[2] += 100*((runtime_energy_greedy-simulation_results_energy_last_sim)/simulation_results_energy_last_sim)
        simulation_results_exectime[2] += time2-time1

        '''

        time1 = time.clock()
        runs_greedy = greedy_algorithms.greedy_scheduling(num_machines, number_of_nodes_in_dag, dag_adj_list_by_index, node_to_application,  rand_wl_scale, applications, power_cap, 50)
        time2 = time.clock()
        runs_greedy.sort(key=lambda x: x.end_time)
        #runs2file(runs_greedy, "greedy-level-" +lookahead_str+"-" +dag_name+".txt")
        idle_energy_greedy = runs_greedy[-1].end_time * idle_pow * num_machines
        runtime_energy_greedy = sum(run.power*(run.end_time - run.start_time) for run in runs_greedy)
        sim_log.log("INFO", "Finish time and total power, time of greedy lookahead " + str(50) + ' : \t\t' + str(int(runs_greedy[-1].end_time)) + ' \t' + str(int(idle_energy_greedy + runtime_energy_greedy))+' = '+str(int(idle_energy_greedy)) + ' + '+str(int(runtime_energy_greedy)) + ' \t\t' + str((time2-time1)))
        #plot.draw_pow_opt("greedy-level-" +lookahead_str+"-"+dag_name, ".txt", power_cap, True, False)
        simulation_results_makespan[3] += runs_greedy[-1].end_time
        simulation_results_energy[3] += runtime_energy_greedy
        simulation_results_makespan_percent[3] += 100*((runs_greedy[-1].end_time - simulation_results_makespan_last_sim)/simulation_results_makespan_last_sim)
        simulation_results_energy_percent[3] += 100*((runtime_energy_greedy-simulation_results_energy_last_sim)/simulation_results_energy_last_sim)
        simulation_results_exectime[3] += time2-time1

        time1 = time.clock()
        runs_greedy = greedy_algorithms.greedy_scheduling(num_machines, number_of_nodes_in_dag, dag_adj_list_by_index, node_to_application, rand_wl_scale, applications, power_cap, 100)
        time2 = time.clock()
        runs_greedy.sort(key=lambda x: x.end_time)
        #runs2file(runs_greedy, "greedy-level-" +lookahead_str+"-" +dag_name+".txt")
        idle_energy_greedy = runs_greedy[-1].end_time * idle_pow * num_machines
        runtime_energy_greedy = sum(run.power*(run.end_time - run.start_time) for run in runs_greedy)
        sim_log.log("INFO", "Finish time and total power, time of greedy lookahead " + str(100) + ' : \t\t' + str(int(runs_greedy[-1].end_time)) + ' \t' + str(int(idle_energy_greedy + runtime_energy_greedy))+' = '+str(int(idle_energy_greedy)) + ' + '+str(int(runtime_energy_greedy)) + ' \t\t' + str((time2-time1)))
        #plot.draw_pow_opt("greedy-level-" +lookahead_str+"-"+dag_name, ".txt", power_cap, True, False)
        simulation_results_makespan[4] += runs_greedy[-1].end_time
        simulation_results_energy[4] += runtime_energy_greedy
        simulation_results_makespan_percent[4] += 100*((runs_greedy[-1].end_time - simulation_results_makespan_last_sim)/simulation_results_makespan_last_sim)
        simulation_results_energy_percent[4] += 100*((runtime_energy_greedy-simulation_results_energy_last_sim)/simulation_results_energy_last_sim)
        simulation_results_exectime[4] += time2-time1
        '''
    optimizelogs = [([]) for i in range(0)]
    taskset=[]
    if DIVIDECONQUER:
        time3 = time.clock()
        runs_dc = divide_and_conquer.divide_and_conquer_scheduler(taskset,optimizelogs,optimize23,machine_to_task_sep,num_machines, 20, number_of_nodes_in_dag, dag_adj_list_by_index, node_to_application, rand_wl_scale, applications, power_cap, random_mid_point  = False)
        time4 = time.clock()
        runs_dc.sort(key=lambda x: x.end_time)
        #runs2file(runs_dc, "d&c-"+dag_name+".txt")
        idle_energy_dc = runs_dc[-1].end_time * idle_pow * num_machines
        runtime_energy_dc = sum(run.power*(run.end_time - run.start_time) for run in runs_dc)
        sim_log.log("INFO", "Finish time and total energy (idle+active), time of D&C:  \t\t" + str(int(runs_dc[-1].end_time)) + ' \t' + str(int(idle_energy_dc + runtime_energy_dc))+' = '+str(int(idle_energy_dc)) + ' + '+str(int(runtime_energy_dc)) + ' \t\t' + str((time4-time3)))
        #plot.draw_pow_opt("d&c-"+dag_name, ".txt", power_cap, True, False)
        simulation_results_makespan[5] += runs_dc[-1].end_time
        simulation_results_energy[5] += runtime_energy_dc
        simulation_results_makespan_percent[5] += 100*((runs_dc[-1].end_time - simulation_results_makespan_last_sim)/simulation_results_makespan_last_sim)
        simulation_results_energy_percent[5] += 100*((runtime_energy_dc-simulation_results_energy_last_sim)/simulation_results_energy_last_sim)
        simulation_results_exectime[5] += time4-time3

        # DC random
        time3 = time.clock()
        random_dc_runtime = float('Inf')
        random_dc_energy = float('Inf')
        optimizelogs = [([]) for i in range(0)]
        taskset = []
        for random_tries in range(1):
            print('finally xunhuan~')
            runs_dc_random = divide_and_conquer.divide_and_conquer_scheduler(taskset,optimizelogs,optimize23,machine_to_task_sep,num_machines, 20, number_of_nodes_in_dag, dag_adj_list_by_index, node_to_application, rand_wl_scale, applications, power_cap, random_mid_point = True)
            runs_dc_random.sort(key=lambda x: x.end_time)
            idle_energy_dc_random = runs_dc_random[-1].end_time * idle_pow * num_machines
            runtime_energy_dc_random = sum(run.power*(run.end_time - run.start_time) for run in runs_dc_random)
            if random_dc_runtime > runs_dc_random[-1].end_time:
                random_dc_runtime = runs_dc_random[-1].end_time
                random_dc_energy = runtime_energy_dc_random
        time4 = time.clock()
        print('1758任务数:',number_of_nodes_in_dag)
        print('runs_dc_random:',runs_dc_random)
        print('finally_machine_to_task_sep:',machine_to_task_sep)
        runs2file(runs_dc_random, "d&c-20201111-random-"+dag_name+".txt")
        sim_log.log("INFO", "1436Finish time and total energy (idle+active), time of D&C Random:  \t" + str(int(random_dc_runtime)) + ' \t' + str(int(random_dc_runtime* idle_pow * num_machines + random_dc_energy))+' = '+str(int(random_dc_runtime* idle_pow * num_machines)) + ' + '+str(int(random_dc_energy))+ ' \t\t' + str((time4-time3)))
        plot.draw_pow_opt("d&c-20201111-random-"+dag_name, ".txt", power_cap, True, False)
        simulation_results_makespan[6] += random_dc_runtime
        simulation_results_energy[6] += random_dc_energy
        simulation_results_makespan_percent[6] += 100*((random_dc_runtime - simulation_results_makespan_last_sim)/simulation_results_makespan_last_sim)
        simulation_results_energy_percent[6] += 100*((random_dc_energy - simulation_results_energy_last_sim)/simulation_results_energy_last_sim)
        simulation_results_exectime[6] += time4-time3

        '''
        #DC Experimental
        time3 = time.clock()
        runs_dc_exp = divide_and_conquer.divide_and_conquer_scheduler(num_machines, int(number_of_nodes_in_dag/num_machines)+1, number_of_nodes_in_dag, dag_adj_list_by_index, node_to_application, rand_wl_scale, applications, power_cap, random_mid_point  = False)
        time4 = time.clock()
        runs_dc_exp.sort(key=lambda x: x.end_time)
        #runs2file(runs_dc, "d&c-"+dag_name+".txt")
        idle_energy_dc = runs_dc_exp[-1].end_time * idle_pow * num_machines
        runtime_energy_dc = sum(run.power*(run.end_time - run.start_time) for run in runs_dc_exp)
        sim_log.log("INFO", "Finish time and total energy (idle+active), time of D&C EXPERIMENTAL:  " + str(int(runs_dc_exp[-1].end_time)) + ' \t' + str(int(idle_energy_dc + runtime_energy_dc))+' = '+str(int(idle_energy_dc)) + ' + '+str(int(runtime_energy_dc)) + ' \t\t' + str((time4-time3)))
        #plot.draw_pow_opt("d&c-"+dag_name, ".txt", power_cap, True, False)
        simulation_results_makespan[7] += runs_dc_exp[-1].end_time
        simulation_results_energy[7] += runtime_energy_dc
        simulation_results_makespan_percent[7] += 100*((runs_dc_exp[-1].end_time - simulation_results_makespan_last_sim)/simulation_results_makespan_last_sim)
        simulation_results_energy_percent[7] += 100*((runtime_energy_dc - simulation_results_energy_last_sim)/simulation_results_energy_last_sim)
        simulation_results_exectime[7] += time4-time3
        '''
    print('optimizelogs:',optimizelogs)
    print('taskset:',taskset)
    with open('taskset.txt', 'w') as f:
        for i in range(len(taskset)):
            f.write(str(taskset[i])+"\n")
    with open('optimizelogs.txt', 'w') as f:
        for i in range(len(optimizelogs)):
            f.write(str(optimizelogs[i])+"  "+str(taskset[i])+"\n")
sim_log.log("INFO", "***************************************")
sim_log.log("INFO", "***************************************")
sim_log.log("INFO", "Simulation Stats, (mean) Mean Pace Tasks Power:" + str(int(simulation_stats[0]/simulation_count)))
sim_log.log("INFO", "Simulation Stats, (mean) Time Weighted Mean Pace Tasks Power:" + str(int(simulation_stats[1]/simulation_count)))
sim_log.log("INFO", "Simulation Stats, (mean) Median Pace Tasks Power:" + str(int(simulation_stats[2]/simulation_count)))
sim_log.log("INFO", "Simulation Stats, (mean) Mean Pace Tasks Time:" + str(int(simulation_stats[3]/simulation_count)))
sim_log.log("INFO", "Simulation Stats, (mean) Median Pace Tasks Time:" + str(int(simulation_stats[4]/simulation_count)))
sim_log.log("INFO", "***************************************")
sim_log.log("INFO", "Simulation Stats, Final Results with num_machines: " + str(num_machines) + ' Power cap: ' + str(power_cap) + ' DAG: ' + str(dag_name) + ' simulation count: ' + str(simulation_count)  )
sim_log.log("INFO", "Finish time and total energy, possible Optimal: \t\t\t\t" + str(int(simulation_results_makespan[8])) + ' \t\t' + str(int(simulation_results_energy[8])) )
sim_log.log("INFO", "Finish time and total energy, time of Naive Grab all Run all, makespan:  \t" + str(int(simulation_results_makespan_percent[9]/simulation_count)) +'%' + '('+ str(int(simulation_results_makespan[9])) +')'+ ' \t Energy (excluding idle) used: ' + str(int(simulation_results_energy_percent[9]/simulation_count)) +'%' + ' ('+ str(int(simulation_results_energy[9])) +')' + ' \t Energy not utilized, permille: ' + str(int(simulation_results_makespan[9]*power_cap - simulation_results_energy[9])) + ' ‰' + str(int(1000*(simulation_results_makespan[9]*power_cap - simulation_results_energy[9])/(simulation_results_makespan[9]*power_cap))) + ' \t in run time: ' + str(int(10*simulation_results_exectime[9])))
sim_log.log("INFO", "Finish time and total energy, time of Greedy lookahead " + str(1) + ' makepsan: \t\t' + str(int(simulation_results_makespan_percent[0]/simulation_count)) +'%' + '('+ str(int(simulation_results_makespan[0])) +')'+ ' \t Energy (excluding idle) used: ' + str(int(simulation_results_energy_percent[0]/simulation_count)) +'%' + ' ('+ str(int(simulation_results_energy[0])) +')'+ ' \t Energy not utilized, permille: ' + str(int(simulation_results_makespan[0]*power_cap - simulation_results_energy[0])) + ' ‰' + str(int(1000*(simulation_results_makespan[0]*power_cap - simulation_results_energy[0])/(simulation_results_makespan[0]*power_cap))) + ' \t in run time: ' + str(int(10*simulation_results_exectime[0])))
sim_log.log("INFO", "Finish time and total energy, time of Greedy lookahead " + str(10) + ' makepsan: \t\t' + str(int(simulation_results_makespan_percent[1]/simulation_count)) +'%' + '('+ str(int(simulation_results_makespan[1])) +')'+ ' \t Energy (excluding idle) used: ' + str(int(simulation_results_energy_percent[1]/simulation_count)) +'%' + ' ('+ str(int(simulation_results_energy[1])) +')'+ ' \t Energy not utilized, permille: ' + str(int(simulation_results_makespan[1]*power_cap - simulation_results_energy[1])) + ' ‰' + str(int(1000*(simulation_results_makespan[1]*power_cap - simulation_results_energy[1])/(simulation_results_makespan[1]*power_cap))) + ' \t in run time: ' + str(int(10*simulation_results_exectime[1])))
sim_log.log("INFO", "Finish time and total energy, time of Greedy lookahead " + str(20) + ' makepsan: \t\t' + str(int(simulation_results_makespan_percent[2]/simulation_count)) +'%' + '('+ str(int(simulation_results_makespan[2])) +')'+ ' \t Energy (excluding idle) used: ' + str(int(simulation_results_energy_percent[2]/simulation_count)) +'%' + ' ('+ str(int(simulation_results_energy[2])) +')'+ ' \t Energy not utilized, permille: ' + str(int(simulation_results_makespan[2]*power_cap - simulation_results_energy[2])) + ' ‰' + str(int(1000*(simulation_results_makespan[2]*power_cap - simulation_results_energy[2])/(simulation_results_makespan[2]*power_cap))) + ' \t in run time: ' + str(int(10*simulation_results_exectime[2])))
#sim_log.log("INFO", "Finish time and total energy, time of Greedy lookahead " + str(50) + ' makepsan: \t\t' + str(int(simulation_results_makespan_percent[3]/simulation_count)) +'%' + '('+ str(int(simulation_results_makespan[3])) +')'+ ' \t Energy (excluding idle) used: ' + str(int(simulation_results_energy_percent[3]/simulation_count)) +'%' + ' ('+ str(int(simulation_results_energy[3])) +')'+ ' \t Energy not utilized, permille: ' + str(int(simulation_results_makespan[3]*power_cap - simulation_results_energy[3])) + ' ‰' + str(int(1000*(simulation_results_makespan[3]*power_cap - simulation_results_energy[3])/(simulation_results_makespan[3]*power_cap))) + ' \t in run time: ' + str(int(10*simulation_results_exectime[3])))
#sim_log.log("INFO", "Finish time and total energy, time of Greedy lookahead " + str(100) + ' makepsan: \t\t' + str(int(simulation_results_makespan_percent[4]/simulation_count)) +'%' + '('+ str(int(simulation_results_makespan[4])) +')'+ ' \t Energy (excluding idle) used: ' + str(int(simulation_results_energy_percent[4]/simulation_count)) +'%' + ' ('+ str(int(simulation_results_energy[4])) +')'+ ' \t Energy not utilized, permille: ' + str(int(simulation_results_makespan[4]*power_cap - simulation_results_energy[4])) + ' ‰' + str(int(1000*(simulation_results_makespan[4]*power_cap - simulation_results_energy[4])/(simulation_results_makespan[4]*power_cap))) + ' \t in run time: ' + str(int(10*simulation_results_exectime[4])))
sim_log.log("INFO", "Finish time and total energy, time of D&C makepsan:  \t\t\t\t" + str(int(simulation_results_makespan_percent[5]/simulation_count)) +'%' + '('+ str(int(simulation_results_makespan[5])) +')'+ ' \t Energy (excluding idle) used: ' + str(int(simulation_results_energy_percent[5]/simulation_count)) +'%' + ' ('+ str(int(simulation_results_energy[5])) +')' + ' \t Energy not utilized, permille: ' + str(int(simulation_results_makespan[5]*power_cap - simulation_results_energy[5])) + ' ‰' + str(int(1000*(simulation_results_makespan[5]*power_cap - simulation_results_energy[5])/(simulation_results_makespan[5]*power_cap))) + ' \t in run time: ' + str(int(10*simulation_results_exectime[5])))
sim_log.log("INFO", "Finish time and total energy, time of D&C RANDOM makepsan:  \t\t\t" + str(int(simulation_results_makespan_percent[6]/simulation_count)) +'%' + '('+ str(int(simulation_results_makespan[6])) +')'+ ' \t Energy (excluding idle) used: ' + str(int(simulation_results_energy_percent[6]/simulation_count)) +'%' + ' ('+ str(int(simulation_results_energy[6])) + ')' + ' \t Energy not utilized, permille: ' + str(int(simulation_results_makespan[6]*power_cap - simulation_results_energy[6])) + ' ‰' + str(int(1000*(simulation_results_makespan[6]*power_cap - simulation_results_energy[6])/(simulation_results_makespan[6]*power_cap))) + ' \t in run time: ' + str(int(10*simulation_results_exectime[6])))
#sim_log.log("INFO", "Finish time and total energy, time of D&C EXPERIMENTAL makepsan:  \t\t" + str(int(simulation_results_makespan_percent[7]/simulation_count)) +'%' + '('+ str(int(simulation_results_makespan[7])) +')'+ ' \t Energy (excluding idle) used: ' + str(int(simulation_results_energy_percent[7]/simulation_count)) +'%' + ' ('+ str(int(simulation_results_energy[7])) + ')' + ' \t Energy not utilized, permille: ' + str(int(simulation_results_makespan[7]*power_cap - simulation_results_energy[7])) + ' ‰' + str(int(1000*(simulation_results_makespan[7]*power_cap - simulation_results_energy[7])/(simulation_results_makespan[7]*power_cap))) + ' \t in run time: ' + str(int(10*simulation_results_exectime[7])))
sim_log.log("INFO", "***************************************")
sim_log.log("INFO", "***************************************")

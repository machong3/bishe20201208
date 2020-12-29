
def func(taskNum):#高
    if(taskNum>=1)and(taskNum<=3):
        return 1
    elif(taskNum>=4)and(taskNum<=6):
        return 6
    else:
        return 6
def DFS(x):
    global sum
    global n
    global pos
    global result
    global tasktime
    global besttasktime
    global bestresult
    global bestpos
    tasktime=0
    if(sum==n):
        '''
        print(n,"=",end='')
        for i in range(pos):
            print(result[i],"+",end='')
        print(result[pos],end='')
        '''
        for i in range(pos+1):
            tasktime=round(tasktime+func(result[i]),1)
        #print("任务时长：",tasktime)
        if(besttasktime==-1.0):
            besttasktime=tasktime
            for i in range(n):
                bestresult[i] = result[i]
            bestpos=pos
        else:
            if(besttasktime>tasktime):
                besttasktime = tasktime
                for i in range(n):
                    bestresult[i] = result[i]
                bestpos = pos
        return
    if(sum>n):
        return
    i=x
    while(i<n+1):
        pos=pos+1
        result[pos]=i
        sum=sum+i
        DFS(i)
        pos=pos-1
        sum=sum-i
        i=i+1

def useit(a):
    global sum
    sum = 0
    global n
    n = a
    global pos
    pos = -1
    global result
    result = [0] * n
    global tasktime
    tasktime=0.0
    global besttasktime
    besttasktime=-1.0
    global bestresult
    bestresult=[0]*n
    global bestpos
    bestpos=-1
    DFS(1)
    print("深度优先搜索最优解：")
    print(n, "=", end='')
    for i in range(bestpos):
        print(bestresult[i], "+", end='')
    print(bestresult[bestpos])
    return bestresult,bestpos






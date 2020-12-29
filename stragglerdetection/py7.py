import pandas as pd
import matplotlib.pyplot as plt
import math
import numpy as np

path='attempt6.csv'
f1=pd.read_csv(path,usecols=['startTime','finishTime','hostname'])
f1.dropna(axis=0, how='any', inplace=True)#消除Nan
list=f1.values.tolist()
print(len(list))
print(list[0])
'''
print(len(list1))
print(list1[0])
print(list1[1])
list=[([0]*3)for i in range(len(list1))]
i=0
while i<len(list1):
    list[i][0]=int(list1[i][0])
    list[i][1]=int(list1[i][1])
    list[i][2]=int(list1[i][2])
    i=i+1
print(len(list))
print(list[0])
print(list[1])
'''
listtime=[]
i=0
while i<len(list):
    listtime.append(list[i][1]-list[i][0])
    i=i+1
sortedlisttime=sorted(listtime)
medianindex=math.ceil(len(sortedlisttime)/2)
mediannumber=sortedlisttime[medianindex]
print('mediannumber:',mediannumber)

time2=[[] for i in range(250)]
i=0
namei=0
while i<len(listtime):
    namei=list[i][2]
    time2[namei].append(listtime[i])
    i=i+1
stragglernum=[0]*250
i=0
namei=0
while i<len(listtime):
    namei = list[i][2]
    if(listtime[i]>mediannumber*1.5):
        stragglernum[namei]=stragglernum[namei]+1
    i=i+1
tasknum=[0]*250
i=0
namei=0
while i<len(listtime):
    namei=list[i][2]
    tasknum[namei]=tasknum[namei]+1
    i=i+1
#save=pd.DataFrame(tasknum)
#save.to_csv("wuyong.csv")
i=0
while i<len(stragglernum):
    print(i,":",tasknum[i])
    i=i+1
print("the program comes here!")

straggleroftask=[0.0]*250
i=0
while i<len(tasknum):
    if(tasknum[i]!=0 and stragglernum[i]>100):
        straggleroftask[i]=stragglernum[i]/tasknum[i]
    i=i+1
#save=pd.DataFrame(stragglernum)
#save.to_csv("write11.csv")
i=0
while i<len(stragglernum):
    print(i,":",straggleroftask[i])
    i=i+1
#save=pd.DataFrame(straggleroftask)
#save.to_csv("straggleroftask\\write1.csv")
print("the program comes here!")

'''
enoughstraggler=[]
i=0
while i<len(stragglernum):
    if(stragglernum[i]>100):
        enoughstraggler.append(stragglernum[i])
    i=i+1
print("enoughstraggler:",enoughstraggler)
print("lengthenoughstraggler:",len(enoughstraggler))
arr_mean=np.mean(enoughstraggler)
arr_std=np.std(enoughstraggler,ddof=1)
print("平均值：",arr_mean)
print("标准差：",arr_std)

i=0
temp=0.0
normalizedstraggler=[0.0]*250
print(normalizedstraggler)
while i<len(stragglernum):
    if(stragglernum[i]>100):
        temp = stragglernum[i]-arr_mean
        normalizedstraggler[i]=temp/arr_std
    i=i+1
print(normalizedstraggler)
#save=pd.DataFrame(normalizedstraggler)
#save.to_csv("normalized\\normalizedwrite6.csv")
print("here!")
'''
#save=pd.DataFrame(stragglernum)
#save.to_csv("write11.csv")
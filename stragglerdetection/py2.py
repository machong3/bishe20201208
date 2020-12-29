import pandas as pd
import matplotlib.pyplot as plt
import math

path='attempt5.csv'
f1=pd.read_csv(path,usecols=['hostname','startTime','finishTime'])
list=f1.values.tolist()
#print(list[1])
listtime=[]
i=0
while i<len(list):
    listtime.append(list[i][1]-list[i][0])
    i=i+1
'''
i=0
a=len(listtime)
while i<a:
    if listtime[i]>100000000000:
       listtime.pop(i)
       list.pop(i)
       a=a-1
       i=i-1
    i=i+1
i=0
a=0
while i<len(listtime):
    if listtime[i]>100000000000:
        a=a+1
    i=i+1
print("奇怪的数个数：",a)
'''
#print(listtime[1])
#f2=pd.read_csv(path,usecols=['hostname'])
#list2=f2.values.tolist()
sortedlisttime=sorted(listtime)
medianindex=math.ceil(len(sortedlisttime)/2)
mediannumber=sortedlisttime[medianindex]
print('mediannumber:',mediannumber)
namelist=[]
i=0
j=0
print("len(list):",len(list))
print("list[0]:",list[0])
print("len(listtime):",len(listtime))
while i<len(list):
    while j<len(namelist):
        if list[i][2]==namelist[j]:
            break
        j=j+1
    if j==len(namelist):
        namelist.append(list[i][2])
    j=0
    i=i+1
print(namelist)
print('len(namelist):',len(namelist))
x=[1,len(namelist)]
y=[mediannumber*1.5,mediannumber*1.5]
plt.plot(x,y)
i=0
time2=[[] for i in range(len(namelist))]
while i<len(listtime):
    j=0
    while j<len(namelist):
        if list[i][2]==namelist[j]:
            break
        j=j+1
    time2[j].append(listtime[i])
    i=i+1
#print('time2[0]:',time2[0])
stragglernum=[0]*len(namelist)
i=0
while i<len(listtime):
    if listtime[i]>=mediannumber*1.5:
        j=0
        while j<len(namelist):
            if list[i][2]==namelist[j]:
                break
            j=j+1
        stragglernum[j]=stragglernum[j]+1
    i=i+1
print("stragglernum:",stragglernum)
print('time2[0]:',time2[0])
plt.boxplot(time2)
plt.show()


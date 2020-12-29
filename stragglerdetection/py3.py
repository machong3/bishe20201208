import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

mpl.rcParams["font.sans-serif"]=["SimHei"]
#指定字体为SimHei，用于显示中文，如果Ariel,中文会乱码
mpl.rcParams["axes.unicode_minus"]=False
#用来正常显示负号



x = np.arange(14) #产生1~8的序列
print(x)
#注意：这里使用numpy库，需要在程序开始时导包“import numpy as np”
yvcenumyidongpingjun=[6629,6984,7065,6781,6832,6458,7050,5261,5222,6817,6541,6709,6833,3143]
yvcenumzhishupinghua=[6311,6721,6281,6319,5954,6313,6591,5377,4800,6332,5969,6515,6509,3671]
yvcenumhuiseyvce=    [5490,8625,8555,7948,7668,8252,8049,10748,8395,7752,5955,7462,8238,9250]
shijinum=            [5417,8136,7885,7941,7751,7836,7974,7743,6254,7165,6132,7741,7943,7857]

y = shijinum#掺杂前/实际
std_err=[200,400,500,600,800,900] #误差棒
y1= yvcenumhuiseyvce#掺杂后/预测
std_err1=[100,200,100,200,100,200] #误差棒
n=len(y)
xiangduiwucha=[0.0]*n
zhunquelv=[0.0]*n
i=0
temp=0
while i<n:
    temp=y1[i]-y[i]
    print(temp)
    xiangduiwucha[i]=abs(temp/y[i])
    zhunquelv[i]=1-xiangduiwucha[i]
    i=i+1
i=0
print("相对误差：",xiangduiwucha)
while i<n:
    xiangduiwucha[i]=round(xiangduiwucha[i]*1000)
    xiangduiwucha[i]=xiangduiwucha[i]/1000
    i=i+1
print("相对误差：",xiangduiwucha)
i=0
print(zhunquelv)
while i<n:
    zhunquelv[i]=round(zhunquelv[i]*1000)
    zhunquelv[i]=zhunquelv[i]/1000
    i=i+1
print(zhunquelv)
#数据
error_attri = dict(elinewidth=1,ecolor="r",capsize=3)
#定义误差棒属性的字典数据。这三个参数分别定义误差棒的线宽、颜色、帽子大小
tick_label=["24","26","27","41","42","43","45","46","52","53","55","56","60","69"]
#定义柱子的标签
bar_width=0.35
#定义柱宽
plt.bar(x,y,bar_width,color="lightgreen",align="center",label="实际值",error_kw=error_attri)
#绘制纵向柱状图,hatch定义柱图的斜纹填充，省略该参数表示默认不填充。
plt.bar(x+bar_width,y1,bar_width,color="c",align="center",label="预测值",lw=0.1,hatch="//////",error_kw=error_attri)

for xx,yy in enumerate(y1):
    plt.text(xx+bar_width,yy+100,'%s' %xiangduiwucha[xx],ha='center')# 显示图形

plt.title('灰色预测法预测结果')
plt.xticks(x+bar_width/2,tick_label)

plt.xlabel("节点ID")
plt.ylabel("慢任务数量")
plt.legend()
plt.show()
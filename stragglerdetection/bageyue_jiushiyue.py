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
yvcenumhuiseyvcejiuyue=[7793,8189,8189,7958,7941,7823,7674,1435,6858,7785,6925,7029,7874,302]
yvcenumhuiseyvceshiyue=[5193,8151,8160,7766,7355,8130,7504,7070,8098,7523,5320,6683,8022,1610]
shijinumjiuyue=        [8543,8936,8656,8267,8607,8014,8799,2912,7333,8272,8591,8654,8307,2211]
shijinumshiyue=        [5417,8136,7885,7941,7751,7836,7974,7743,6254,7165,6132,7741,7943,7857]

y = shijinumjiuyue#掺杂前/实际
std_err=[200,400,500,600,800,900] #误差棒
y1= yvcenumhuiseyvcejiuyue#掺杂后/预测
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

plt.title('灰色预测法预测结果(九月份)')
plt.xticks(x+bar_width/2,tick_label)

plt.xlabel("节点ID")
plt.ylabel("慢任务数量")
plt.legend(loc=2, bbox_to_anchor=(1.05,1.0),borderaxespad = -0.2)
plt.show()
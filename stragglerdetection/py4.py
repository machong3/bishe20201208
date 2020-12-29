import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

mpl.rcParams["font.sans-serif"]=["SimHei"]
#指定字体为SimHei，用于显示中文，如果Ariel,中文会乱码
mpl.rcParams["axes.unicode_minus"]=False
#用来正常显示负号



x = np.arange(8) #产生1~8的序列
print(x)
#注意：这里使用numpy库，需要在程序开始时导包“import numpy as np”
y = [10,11,22,33,41,58,62,75]#掺杂前
std_err=[2,4,5,6,8,9,8,6] #误差棒
y1= [15,23,44,67,88,99,95,85]#掺杂后
std_err1=[1,2,1,2,1,2,3,2] #误差棒
#数据
error_attri = dict(elinewidth=1,ecolor="r",capsize=3)
#定义误差棒属性的字典数据。这三个参数分别定义误差棒的线宽、颜色、帽子大小
tick_label=["A","B","C","D","E","F","G","H"]
#定义柱子的标签
bar_width=0.35
#定义柱宽
plt.bar(x,y,bar_width,color="lightgreen",align="center",label="掺杂前",yerr=std_err,error_kw=error_attri)
#绘制纵向柱状图,hatch定义柱图的斜纹填充，省略该参数表示默认不填充。
plt.bar(x+bar_width,y1,bar_width,color="c",align="center",label="掺杂后",lw=0.1,hatch="//////",yerr=std_err1,error_kw=error_attri)

plt.xticks(x+bar_width/2,tick_label)

plt.xlabel("样品编号")
plt.ylabel("降解率/%")
plt.legend()
plt.show()
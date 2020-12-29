import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

mpl.rcParams["font.sans-serif"]=["SimHei"]
mpl.rcParams["axes.unicode_minus"]=False
x = np.arange(6)
print(x)
#注意：这里使用numpy库，需要在程序开始时导包“import numpy as np”
yvcenumyidongpingjun=[6629,6984,7065,6781,6832,6458]
yvcenumzhishupinghua=[6311,6721,6281,6319,5954,6313]
yvcenumhuiseyvce=    [5490,8625,8555,7948,7668,8252]
shijinum=            [5417,8136,7885,7941,7751,7836]
tick_label=["24","26","27","41","42","43"]
bar_width=0.2
plt.bar(x,shijinum,bar_width,color="lightgreen",align="center",label="实际值")
plt.bar(x+bar_width,yvcenumhuiseyvce,bar_width,color="c",align="center",label="灰色预测",lw=0.1,hatch="//////")
plt.bar(x+bar_width*2,yvcenumyidongpingjun,bar_width,color="r",align="center",label="移动平均",lw=0.1,hatch="//////")
plt.bar(x+bar_width*3,yvcenumzhishupinghua,bar_width,color="b",align="center",label="指数平滑",lw=0.1,hatch="//////")
plt.title('预测结果对比')
plt.xticks(x+bar_width/2+bar_width,tick_label)

plt.xlabel("节点ID")
plt.ylabel("慢任务数量")
plt.legend(loc=2, bbox_to_anchor=(1.05,1.0),borderaxespad = -0.2)
plt.show()
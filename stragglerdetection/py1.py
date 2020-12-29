import matplotlib.pyplot as plt
x = [1,2,3,5]   				#数据集
y=[4,3,7,9]
z=[2,4,8]

# 中文乱码的处理
plt.rcParams['font.sans-serif'] =['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

shiji=[0.415,0.411,0.401,0.401,0.397,0.393]
yvce=[0.4203,0.4353,0.4353,0.4017,0.3924,0.4136]

tasknum6=[13061,19814,19652,19785,19541,19951]

yvcenum=[5490,8625,8555,7948,7668,8252]
yvcenumyidongpingjun=[6629,6984,7065,6781,6832,6458]
yvcenumzhishupinghua=[6311,6721,6281,6319,5954,6313]
shijinum=[5417,8136,7885,7941,7751,7836]


plt.bar([1,3,5,7,9,11],shijinum)
plt.bar([2,4,6,8,10,12],yvcenumzhishupinghua,color='red')
plt.ylabel('stragglerNUM')
plt.xticks(range(4),['北京市','上海市','天津市','重庆市'])

#plt.boxplot((x,y,z),labels=('x','y','z'))    				#垂直显示箱线图
plt.show()						#显示该图
import matplotlib.pyplot as plt #use for drawing
import matplotlib.patches as patches #use for drawing
import os
from operator import itemgetter
from app_file_handler import idle_power
import random

power_cap = 200 #make sure this is the power cap used during simulation...
outDir = os.path.join(os.getcwd(), "output", "charts")
inDir = os.path.join(os.getcwd(), "output")

colors = ['#FF0000','#0000FF','#006400',
          '#FFD700','#B22222','#4B0082',
          '#008000','#FFA500','#800000',
          '#008B8B','#808000','#DAA520',
          '#FF00FF','#00FFFF','#00FF00',
          '#D2691E','#FF1493','#008080',
          '#556B2F','#D8BFD8','#8B4513',
          '#000080','#00FF7F','#BDB76B',
          '#CD5C5C','#1E90FF','#FF7F50']

random.shuffle(colors)


def add_rectangle(ax, x, y, w, h, col='#0F56CC'):
    ax.add_patch(
        patches.Rectangle(
            (x,y), w, h,
            edgecolor ="none",
            linewidth=0.1,
            #rasterized=True,
            color = col
            )
        )

idle_pow = 90 #the idle power of each machine

def draw(ax, file_name, file_format, powercap, colored, include_idle):
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Power (W)')
    file = open(os.path.join(inDir,file_name+file_format), 'r')
    lines = file.readlines()
    max_time = 0
    for line in lines:
        line = line.split('\t')
        start_time = float(line[0])
        end_time = float(line[1])
        if end_time >= max_time:
            max_time = end_time
        pow_start = float(line[2]) #- idle_pow
        pow_end = float(line[3]) #- idle_pow
        if include_idle:
            pow_start += idle_power
            pow_start += idle_power
        w = end_time - start_time
        h = pow_end - pow_start
        x = start_time
        y = pow_start
        if colored:
            add_rectangle(ax, x, y, w, h, colors[int(line[len(line)-1]) % len(colors)])
        else:
            add_rectangle(ax, x, y, w, h)
    file.close()
    if include_idle:
        add_rectangle(ax, 0, 0, max_time, idle_power, "#bebebe")
    ax.axhline(y = powercap, c = 'r', linewidth = 1, zorder = 5)
    #plt.axis((0, max_time + 10, 0, powercap))
    offset = 5
    ax.spines['left'].set_position(('outward', offset))
    ax.spines['bottom'].set_position(('outward', offset))
    plt.xlim(0, max_time +10)
    #plt.ylim(0, power_cap + 10)
    return max_time


def draw_pow_opt(file_name, file_format, powercap, colored = False, include_idle = False):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_title(file_name)
    max1 = draw(ax, file_name, file_format, powercap, colored, include_idle)
    plt.show()
    fig.savefig(os.path.join(outDir, file_name+"_oldPlot" +".pdf"), bbox_inches='tight')

if __name__ == "__main__":
    file_name = "dc-fans_example"
    draw_pow_opt(file_name, ".txt", power_cap, True, False)

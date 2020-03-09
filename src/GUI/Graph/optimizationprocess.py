import matplotlib.pyplot as plt
import numpy as np

def PlotData(process_data,style,color):
    plt.plot(process_data[2],process_data[1], style,color=color,label=process_data[0])
    # 绘制图形的x轴和y轴的轴名称
    plt.xlabel('generation')
    plt.ylabel('average time')
    # 绘制图形的标题
    plt.title('Algorithm comparision')

    # 显示图形的图例
    plt.legend()

def ShowData():
    plt.show()
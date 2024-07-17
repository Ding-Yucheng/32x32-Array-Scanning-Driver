import time, socket, csv, niswitch, pyvisa
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
from pathlib import Path
import matplotlib as mpl
from matplotlib import ticker, cm
from itertools import islice
import matplotlib.pyplot as plt


UDP_IP = '127.0.0.2'
UDP_Port = 9100


def keiread(fileName):
    kei.write("smu.measure.read()")
    curr = (kei.query("print(defbuffer1.readings[defbuffer1.endindex])"))
    return curr

def scan():
    for i in range(32): #Loop multiplexer
        colChannel = "ch"+str(i)
        mux[0].connect(channel1=colChannel, channel2='com0')
        for j in range(32):
            rowChannel = "ch"+str(j+64)
            mux[0].connect(channel1=rowChannel, channel2='com4')
            for t in range(1):
                curr = keiread(fileName)
                data = np.array(["{:.2f}".format(time.time()),i,j,float(curr)])
                write_csv(fileName, data)
                time.sleep(1)
            raw_data[i][j] = float(curr)
            mux[0].disconnect(channel1=rowChannel, channel2='com4')
        print(i)
        mux[0].disconnect(channel1=colChannel, channel2='com0')
    

def plot_heatmap(data, title="Heatmap", color_map="viridis"):
    """
    绘制热力图的函数

    参数:
    data: 二维数组
    title: 图的标题
    color_map: 颜色映射
    """
    plt.imshow(data, cmap=color_map)
    plt.colorbar()
    plt.title(title)
    plt.show()

def save_to_csv(array, filename):
    """
    将二维数组保存为 CSV 文件。
    
    参数:
    array (list of lists): 二维数组
    filename (str): 要保存的 CSV 文件名
    """
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(array)
 
#isnt initial
rm = pyvisa.ResourceManager()
intList = rm.list_resources()
print(intList)
kei = rm.open_resource(intList[0]) #'USB0::0x05E6::0x2450::04472599::keiR')
print(kei.query("*IDN?"))

#Functions
timestr = time.strftime("%Y%m%d_%H%M%S")
folder = 'compeye_data'
fileName = folder+"/compeye_"+timestr+".csv"
Path(folder).mkdir(parents=True, exist_ok=True)
def write_csv(fileName,data):
    with open(fileName, 'a') as outfile:
        writer = csv.writer(outfile,  lineterminator='\n')
        writer.writerow(data)

#initializing NI box
mux=[]
mux.append(niswitch.Session(resource_name="PXI1Slot9", topology="2530/1-Wire Dual 64x1 Mux"))
print('PXI-mux init ok')

mux[0].reset()
time.sleep(1)

raw_data = np.zeros((32, 32))

fig = plt.figure(figsize = (10, 8))

scan()
save_to_csv(raw_data,folder+"/compeye_"+time.strftime("%Y%m%d_%H%M%S")+"Fig.csv")
plt.ioff()
plt.clf()
plot_heatmap(raw_data)
while False:
    scan()
    plt.ioff()
    plt.clf()
    plot_heatmap(raw_data)
    plt.pause(0.1)

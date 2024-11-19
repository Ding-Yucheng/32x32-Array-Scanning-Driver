import time, socket, csv, niswitch, pyvisa
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
from pathlib import Path
import matplotlib as mpl
from matplotlib import ticker, cm
from itertools import islice
import matplotlib.pyplot as plt
import pandas as pd


UDP_IP = '127.0.0.2'
UDP_Port = 9100


def keiread(fileName):
    kei.write("smu.measure.read()")
    curr = (kei.query("print(defbuffer1.readings[defbuffer1.endindex])"))
    return curr

def scan():
    sttime = time.time()
    #keitime = 0
    for i in range(32): #Loop multiplexer
        
        colNo = (i%2)*16 + int(i/2)
        '''
        if colNo % 2:
            colNo -= 1
        else:
            colNo += 1
        
        
        if i % 2:
            colNo = int(i / 2)
        else:
            colNo = int(i / 2) + 16
        if colNo % 2:
            colNo -= 1
        else:
            colNo += 1
        '''
        colChannel = "ch"+str(colNo)
        mux[0].connect(channel1=colChannel, channel2='com0')
        for j in range(32):
            
            rowNo = (j%2)*16+int(j/2)+64
            '''
            if rowNo % 2:
                rowNo -= 1
            else:
                rowNo += 1
            
            
            if j % 2:
                rowNo = int(j / 2) + 64
            else:
                rowNo = int(j / 2) + 16 + 64
            if rowNo % 2:
                rowNo -= 1
            else:
                rowNo += 1
            '''
            rowChannel = "ch"+str(rowNo)
            mux[0].connect(channel1=rowChannel, channel2='com4')
            for t in range(1):
                #keist = time.time()
                curr = keiread(fileName)
                #keitime += (time.time()-keist)
                data = np.array(["{:.2f}".format(time.time()),i,j,float(curr)])
                write_csv(fileName, data)
            if mode == 3:
                if on[j][31-i] > -0.0000002:
                    raw_data[j][31-i] = 0
                else:
                    raw_data[j][31-i] = (float(curr)-off[j][31-i])/(on[j][31-i]-off[j][31-i])
            else:
                raw_data[j][31-i] = float(curr)
            mux[0].disconnect(channel1=rowChannel, channel2='com4')
        print(i)
        mux[0].disconnect(channel1=colChannel, channel2='com0')
    print(time.time()-sttime)
    #print(keitime)

def plot_heatmap(data, filename, title="Heatmap", color_map="viridis"):
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
    plt.savefig(filename, dpi=300, bbox_inches='tight')
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
bias = '-200mV'
fileName = folder+"/compeye_"+timestr+'_'+bias+".csv"
Path(folder).mkdir(parents=True, exist_ok=True)
def write_csv(fileName,data):
    with open(fileName, 'a') as outfile:
        writer = csv.writer(outfile,  lineterminator='\n')
        writer.writerow(data)

#initializing NI box
mux=[]
mux.append(niswitch.Session(resource_name="PXI1Slot9"))
print('PXI-mux2 init ok')
mux[0].reset()

time.sleep(1)


mode = 0 # 0 for direct scan, 1 for dark current, 2 for light current, 3 for relative scan

raw_data = np.zeros((32, 32))

fig = plt.figure(figsize = (10, 8))

if mode == 3:
    df = pd.read_csv(folder+'/baseline_dark.csv',header=None)
    off = df.values
    df = pd.read_csv(folder+'/baseline_light.csv',header=None)
    on = df.values

scan()
if mode == 1:
    save_to_csv(raw_data, folder+"/baseline_dark.csv")
if mode == 2:
    save_to_csv(raw_data, folder+"/baseline_light.csv")
if mode == 0:
    save_to_csv(raw_data,folder+"/compeye_"+time.strftime("%Y%m%d_%H%M%S")+'_'+bias+"_Fig.csv")
if mode == 3:
    save_to_csv(np.hstack((raw_data, off, on)),folder+"/compeye_"+time.strftime("%Y%m%d_%H%M%S")+'_'+bias+"_Fig_rf.csv")
plt.ioff()
plt.clf()
pngname= folder+"/compeye_"+time.strftime("%Y%m%d_%H%M%S")+'_'+bias+'.png'
plot_heatmap(raw_data, pngname)

while False:
    scan()
    plt.ioff()
    plt.clf()
    plot_heatmap(raw_data)
    plt.pause(0.1)

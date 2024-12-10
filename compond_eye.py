from machine import Pin, DAC, I2C, UART
from ads1x15 import ADS1115
import time,os

# 全局变量用于存储传感器数据
sensor_data = [[0 for _ in range(32)] for _ in range(32)]
row_mask = [19, 2, 17, 0, 23, 6, 21, 4, 27, 10, 25, 8, 31, 14, 29, 12, 13, 28, 15, 30, 9, 24, 11, 26, 5, 20, 7, 22, 1, 16, 3, 18]
col_mask = [3, 18, 1, 16, 7, 22, 5, 20, 11, 26, 9, 24, 15, 30, 13, 28, 29, 12, 31, 14, 25, 8, 27, 10, 21, 4, 23, 6, 17, 0, 19, 2]

##########MUX INITIALIZING##########
Pin_R0 = Pin(12, mode=Pin.OUT, value=0)  # rows
Pin_R1 = Pin(13, mode=Pin.OUT, value=0)
Pin_R2 = Pin(15, mode=Pin.OUT, value=0)
Pin_R3 = Pin(27, mode=Pin.OUT, value=0)
Pin_R4 = Pin(14, mode=Pin.OUT, value=0)
R_Pins = [Pin_R0, Pin_R1, Pin_R2, Pin_R3, Pin_R4]

Pin_C0 = Pin(18, mode=Pin.OUT, value=0)  # columns
Pin_C1 = Pin(33, mode=Pin.OUT, value=0)
Pin_C2 = Pin(25, mode=Pin.OUT, value=0)
Pin_C3 = Pin(5, mode=Pin.OUT, value=0)
Pin_C4 = Pin(17, mode=Pin.OUT, value=0)
C_Pins = [Pin_C0, Pin_C1, Pin_C2, Pin_C3, Pin_C4]
####################################

##########DAC INITIALIZING##########
Pin_DAC = Pin(26, Pin.OUT)
dac = DAC(Pin_DAC)
####################################

##########ADC INITIALIZING##########
Pin_sda = Pin(21, Pin.OUT)
Pin_scl = Pin(22, Pin.OUT)
i2c = I2C(1, scl=Pin_scl, sda=Pin_sda)

adc = ADS1115(i2c, 0x48, 1)
adc.set_conv(3, 1, None)
####################################

Pin_HL_Switch = Pin(16, mode=Pin.OUT)  # initialize pin controlling HL switch
Pin_HL_Switch.value(0)  # 0 for low-freq, 1 for high-freq


def select(pins, index):
    for i in range(5):
        pins[i].value(index & (1 << i))


def scan():
    t = time.time()
    dac.write(95)
    for i in range(32):
        select(R_Pins, row_mask[i])
        for j in range(32):
            select(C_Pins, col_mask[j])
            # time.sleep(0.01)#stablize, this number could be adjusted
            value = adc.read_rev()
            sensor_data[i][j] = value
            # print(value)
            # print(i, j, adc.raw_to_v(value))

    dac.write(0)
    print(time.time() - t)


def list_to_str(data):
    sarr = 'str'
    for line in data:
        for i in line:
            sarr += str(i)
            sarr += '.'
    sarr += 'end'
    return sarr

def save_data_as_csv(data):
    # 构建文件路径
    file_path = 'sensor_data.csv'
    csv_content = ""
    # 构建CSV内容，先添加头部
    csv_content += "row,col,value\n"
    for row in range(len(data)):
        for col in range(len(data[row])):
            csv_content += f"{row},{col},{data[row][col]}\n"

    with open(file_path, 'w') as f:
        f.write(csv_content)

while True:
    scan()
    save_data_as_csv(sensor_data)
import machine
import time
from machine import Pin, I2C
import ads1x15


col_switch = machine.Pin(32, machine.Pin.OUT) # 1: col_mux1; 0: col_mux2
col_a0 = machine.Pin(33, machine.Pin.OUT)
col_a1 = machine.Pin(25, machine.Pin.OUT)
col_a2 = machine.Pin(5, machine.Pin.OUT)
col_a3 = machine.Pin(17, machine.Pin.OUT)
col_code = [col_switch, col_a0, col_a1, col_a2, col_a3]

row_switch = machine.Pin(12, machine.Pin.OUT) # 1: row_mux1; 0: row_mux2
row_a0 = machine.Pin(13, machine.Pin.OUT)
row_a1 = machine.Pin(15, machine.Pin.OUT)
row_a2 = machine.Pin(27, machine.Pin.OUT)
row_a3 = machine.Pin(14, machine.Pin.OUT)
row_code = [row_switch, row_a0, row_a1, row_a2, row_a3]

i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)

# ADS1115默认地址
ADS1115_ADDRESS = 0x48

# ADS1115寄存器
ADS1115_CONVERSION_REG = 0x00
ADS1115_CONFIG_REG = 0x01

def read_ads1115():
    data = i2c.readfrom_mem(ADS1115_ADDRESS, ADS1115_CONVERSION_REG, 2)
    raw_adc = int.from_bytes(data, 'big')
    # 如果结果为负数
    if raw_adc & 0x8000:
        raw_adc -= 1 << 16
    # 根据FSR计算实际电压值
    voltage = raw_adc * 4.096 / 32768
    return voltage

# 读取并打印电压值
voltage = read_ads1115()
print("Voltage:", voltage, "V")

def select(index, mux, pin):
    index = coord[index]
    for m in mux:
        m.value(0)
    mux[index % 2].value(1)
    index = int(index / 2)
    for p in pin:
        p.value(index % 2)
        index = int (index / 2)


'''
for col in range(32):
    select(col, LMUX_list, LA_list)
    for row in range(32):
        select(row, RMUX_list, RA_list)
        for i in range(10):
            time.sleep_ms(1)
            reading = adc.read()
        reading = adc.read()
        print(int(100*reading/4096), end = ',')
    print()
time.sleep(1000)'''
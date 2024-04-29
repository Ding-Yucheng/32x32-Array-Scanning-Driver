import machine
import time
from machine import Pin, I2C, DAC
from ads1x15 import ADS1115

class MyMCU:
    row_masks = [
    [1, 16, 9, 24, 5, 20, 13, 28, 3, 18, 11, 26, 7, 22, 15, 30, 14, 31, 6, 23, 10, 27, 2, 19, 12, 29, 4, 21, 8, 25, 0, 17], # First pin in U1
    [1, 16, 3, 18, 5, 20, 7, 22, 9, 24, 11, 26, 13, 28, 15, 30, 31, 14, 29, 12, 27, 10, 25, 8, 23, 6, 21, 4, 19, 2, 17, 0]  # First pin in U3
    ]
    col_masks = [
    [0, 17, 8, 25, 4, 21, 12, 29, 2, 19, 10, 27, 6, 23, 14, 31, 15, 30, 7, 22, 11, 26, 3, 18, 13, 28, 5, 20, 9, 24, 1, 16], # First pin in U2
    [17, 0, 19, 2, 21, 4, 23, 6, 25, 8, 27, 10, 29, 12, 31, 14, 15, 30, 13, 28, 11, 26, 9, 24, 7, 22, 5, 20, 3, 18, 1, 16]  # First pin in U4
    ]
    def __init__(self, row_type, col_type):
        # Initialize Multiplexers
        self.init_pins()
        self.row_mask = MyMCU.row_masks[row_type]
        self.col_mask = MyMCU.col_masks[col_type]
        
        # Initialize ADC
        adc_i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
        self.adc = ADS1115(adc_i2c, 0x48, 0)
        
        self.mode = machine.Pin(16, machine.Pin.OUT) # 0: Low Freq; 1: High Freq
        self.mode.value(0)
        
        # Initialize DAC
        self.dac = machine.DAC(machine.Pin(26, machine.Pin.OUT), bits = 8)
        
        # Initialize Image Data Array
        self.image = [[0 for _ in range(32)] for _ in range(32)]
    
    def init_pins(self):
        self.row_switch = machine.Pin(12, machine.Pin.OUT)
        self.row_pins = [machine.Pin(pin, machine.Pin.OUT) for pin in [14, 27, 15, 13, 12]]
        self.col_switch = machine.Pin(32, machine.Pin.OUT)
        self.col_pins = [machine.Pin(pin, machine.Pin.OUT) for pin in [17, 5, 25, 33, 32]]
    
    def mode_switch(self, hl):
        self.mode.value(hl)

    def show_adc_reading(self):
        voltage = self.adc.raw_to_v(self.adc.read(channel1 = 1))
        print(voltage)

    @staticmethod
    def number_to_binary_array(index):
        if 0 <= index <= 31:
            return [(index >> bit) & 1 for bit in range(5)]
        else:
            raise ValueError("Number is not in the range 0 to 31.")

    def set_mux(self, pins, index):
        binary_array = self.number_to_binary_array(index)
        for i in range(5):
            pins[i].value(binary_array[i])

    def select(self, r, c):
        self.set_mux(self.row_pins, self.row_mask[r])
        self.set_mux(self.col_pins, self.col_mask[c])
    
    def scan(self):
        for i in range(32):
            self.set_mux(self.row_pins, self.row_mask[i])
            for j in range(32):
                self.set_mux(self.col_pins, self.col_mask[j])
                time.sleep_ms(1)
                self.image[i][j] = self.adc.raw_to_v(self.adc.read(channel1 = 1))
                
    def set_dac(self, voltage):
        self.dac.write(int(255 * voltage / 3.3))
        
row_type = 0
col_type = 0
my_mcu = MyMCU(row_type, col_type)
my_mcu.select(16,16)
time.sleep(10000)
"""
my_mcu.set_dac(0.5)
my_mcu.scan()
print(my_mcu.image)
filename = 'data.csv'

# 打开文件，准备写入
with open(filename, 'w') as file:
    for row in my_mcu.image:
        # 将每一行数据转换为逗号分割的字符串
        row_str = ','.join(str(item) for item in row)
        # 写入一行数据，并添加换行符
        file.write(row_str + '\n')"""
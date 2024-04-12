import machine
import time
from machine import Pin, I2C, DAC
from ads1x15 import ADS1115

class MyMCU:
    row_masks = [
    [16, 1, 18, 3, 20, 5, 22, 7, 24, 9, 26, 11, 28, 13, 30, 15, 14, 31, 12, 29, 10, 27, 8, 25, 6, 23, 4, 21, 2, 19, 0, 17], # First pin in U1
    [1, 16, 3, 18, 5, 20, 7, 22, 9, 24, 11, 26, 13, 28, 15, 30, 31, 14, 29, 12, 27, 10, 25, 8, 23, 6, 21, 4, 19, 2, 17, 0]  # First pin in U3
    ]
    col_masks = [
    [0, 17, 2, 19, 4, 21, 6, 23, 8, 25, 10, 27, 12, 29, 14, 31, 30, 15, 28, 13, 26, 11, 24, 9, 22, 7, 20, 5, 18, 3, 16, 1], # First pin in U2
    [17, 0, 19, 2, 21, 4, 23, 6, 25, 8, 27, 10, 29, 12, 31, 14, 15, 30, 13, 28, 11, 26, 9, 24, 7, 22, 5, 20, 3, 18, 1, 16]  # First pin in U4
    ]

    def __init__(self, row_type, col_type):
        # Initialize Multiplexers
        self.init_pins()
        self.row_mask = MyMCU.row_masks[row_type]
        self.col_mask = MyMCU.col_masks[col_type]
        
        # Initialize ADC
        adc_i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
        self.adc = ADS1115(adc_i2c, 0x48, 1)
        
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
        print("Voltage:", voltage, "V")

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
col_type = 1
my_mcu = MyMCU(row_type, col_type)
my_mcu.select(16,16)
for i in range(3):
    my_mcu.set_dac(3)
    my_mcu.show_adc_reading()
    time.sleep(1)
import machine
import time
from machine import Pin, I2C
import ads1x15

class MyMCU:
    def __init__(self, row_type, col_type):
        # Initialize Multiplexers
        self.row_switch = machine.Pin(12, machine.Pin.OUT) # U1 and U3 1: U3; 0: U1
        self.row_a0 = machine.Pin(13, machine.Pin.OUT)
        self.row_a1 = machine.Pin(15, machine.Pin.OUT)
        self.row_a2 = machine.Pin(27, machine.Pin.OUT)
        self.row_a3 = machine.Pin(14, machine.Pin.OUT)
        self.row_pins = [self.row_a3, self.row_a2, self.row_a1, self.row_a0, self.row_switch]
        row_masks = [
            [16, 1, 18, 3, 20, 5, 22, 7, 24, 9, 26, 11, 28, 13, 30, 15, 14, 31, 12, 29, 10, 27, 8, 25, 6, 23, 4, 21, 2, 19, 0, 17], # First pin in U1
            [1, 16, 3, 18, 5, 20, 7, 22, 9, 24, 11, 26, 13, 28, 15, 30, 31, 14, 29, 12, 27, 10, 25, 8, 23, 6, 21, 4, 19, 2, 17, 0]  # First pin in U3
        ]

        self.col_switch = machine.Pin(32, machine.Pin.OUT) # U2 and U4, 1: U4; 0: U2
        self.col_a0 = machine.Pin(33, machine.Pin.OUT)
        self.col_a1 = machine.Pin(25, machine.Pin.OUT)
        self.col_a2 = machine.Pin(5, machine.Pin.OUT)
        self.col_a3 = machine.Pin(17, machine.Pin.OUT)
        self.col_pins = [self.col_a3, self.col_a2, self.col_a1, self.col_a0, self.col_switch]
        col_masks = [
            [0, 17, 2, 19, 4, 21, 6, 23, 8, 25, 10, 27, 12, 29, 14, 31, 30, 15, 28, 13, 26, 11, 24, 9, 22, 7, 20, 5, 18, 3, 16, 1], # First pin in U2
            [17, 0, 19, 2, 21, 4, 23, 6, 25, 8, 27, 10, 29, 12, 31, 14, 15, 30, 13, 28, 11, 26, 9, 24, 7, 22, 5, 20, 3, 18, 1, 16]  # First pin in U4
        ]

        self.row_mask = row_masks[row_type]
        self.col_mask = col_masks[col_type]
        
        # Initialize ADC
        adc_i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
        self.adc = ads1x15.ADS1115(adc_i2c, 72, 1)
        
        # Initialize Image Data Array
        self.image = [[0 for _ in range(32)] for _ in range(32)]
    
    def show_adc_reading(self):
        voltage = self.adc.read(channel1 = 0)
        print("Voltage:", voltage, "V")

    def number_to_binary_array(index):
        if 0 <= index <= 31:
            binary_str = bin(number)[2:]
            binary_str = binary_str.zfill(5)
            binary_array = [int(bit) for bit in binary_str]
            return binary_array
        else:
            raise ValueError("Number is not in the range 0 to 31.")

    def set_mux(self, index, pins):
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
                self.image[i][j] = self.adc.read(channel1 = 0)
        

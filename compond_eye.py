from machine import Pin, DAC, I2C, UART
from ads1x15 import ADS1115
import time


############ Setting ###############
freq = 0 # 0 for low-freq, 1 for high-freq
scan_interval = 10 # ms
discard_sampling = 10
sampling_number = 3
single_channel_mode = False
voltage = 0.0 # Volt
adc_gain = 2
'''
    0: 6.144 V,  2/3x
    1: 4.096 V,  1x
    2: 2.048 V,  2x
    3: 1.024 V,  4x
    4: 0.512 V,  8x
    5: 0.256 V,  16x
'''
adc_speed = 7
'''
    0: 8 SPS
    1: 16 SPS
    2: 32 SPS
    3: 64 SPS
    4: 128 SPS
    5: 250 SPS
    6: 475 SPS
    7: 860 SPS
'''
####################################

voltage = int(voltage*102)
row_mask = [19, 2, 17, 0, 23, 6, 21, 4, 27, 10, 25, 8, 31, 14, 29, 12, 13, 28, 15, 30, 9, 24, 11, 26, 5, 20, 7, 22, 1, 16, 3, 18]
col_mask = [3, 18, 1, 16, 7, 22, 5, 20, 11, 26, 9, 24, 15, 30, 13, 28, 29, 12, 31, 14, 25, 8, 27, 10, 21, 4, 23, 6, 17, 0, 19, 2]
#########UART INITIALIZING##########
uart = UART(1, baudrate=115200, bits=8, parity=None, stop=1)
####################################

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

adc = ADS1115(i2c, 0x48, adc_gain)
####################################

Pin_HL_Switch = Pin(16, mode=Pin.OUT)  # initialize pin controlling HL switch
Pin_HL_Switch.value(freq) # 0 for low-freq, 1 for high-freq

sensor_data = [[0 for _ in range(32)] for _ in range(32)]

def select(pins, index):
    for i in range(5):
        pins[i].value(index & (1 << i))


def scan():
    t = time.time()
    dac.write(voltage)
    for i in range(32):
        select(R_Pins, row_mask[i])
        for j in range(32):
            select(C_Pins, col_mask[j])
            time.sleep_ms(scan_interval)
            for rep in range(discard_sampling):
                adc.read(adc_speed, 1, None)
            value = 0
            for rep in range(sampling_number):
                value += adc.read(adc_speed, 1, None)
            sensor_data[i][j] = int(value / sampling_number)

    dac.write(0)
    print(f"Frame time: {time.time() - t} seconds")


def list_to_str(data):
    sarr = 'str'
    for line in data:
        for i in line:
            sarr += str(i)
            sarr += '.'
    sarr += 'end'
    return sarr

if single_channel_mode and not freq:
    dac.write(voltage)
    select(R_Pins, row_mask[4])
    select(C_Pins, col_mask[24])
    while True:
        print(adc.read(adc_speed, 1, None))
        time.sleep(0.1)

while not freq:
    if uart.any():
        time.sleep(0.01)
        command = uart.readline().decode('utf-8').strip()
        print("Serial Received: ", command)
        if command == "scan":
            print("Scanning...")
            scan()
            data_to_send = list_to_str(sensor_data).encode('utf-8')
            try:
                uart.write(data_to_send)
                print("data sent!")
                #print(data_to_send)
            except Exception as e:
                print("Serial Error: ", e)
if freq:
    dac.write(voltage)
    select(R_Pins, row_mask[4])
    select(C_Pins, col_mask[24])
    time.sleep(100000)

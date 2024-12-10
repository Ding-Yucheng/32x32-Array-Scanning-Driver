from machine import Pin,DAC,I2C
from ads1x15 import ADS1115
import time
import usocket as socket
import esp
import bluetooth

#######BLUETOOTH INITIALIZING#######
# 激活蓝牙并设置为可被发现
ble = bluetooth.BLE()
ble.active(True)

# 定义服务UUID和特性UUID（自定义，确保唯一性，符合规范）
service_uuid = bluetooth.UUID('12345678-1234-1234-cdef-123456789abc')
char_uuid_tx = bluetooth.UUID('87654321-1234-1234-cdef-123456789abc')
char_uuid_rx = bluetooth.UUID('76543210-1234-1234-cdef-123456789abc')

# 创建蓝牙服务及特性，设置特性为可读可写（可根据需求调整属性）
service = (
    (service_uuid, (
        (char_uuid_tx, bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY,),
        (char_uuid_rx, bluetooth.FLAG_WRITE, ),
    )),
)
((char_handle_tx, char_handle_rx),) = ble.gatts_register_services(service)


name = 'ESP32_COMPEYE'
adv_data = bytearray(b'\x02\x01\x06') + bytearray((len(name) + 1, 0x09)) + bytearray(name, 'utf - 8')
ble.gap_advertise(100, adv_data)

def send_data(data):
    ble.gatts_write(char_handle_tx, data)


def receive_data():
    return ble.gatts_read(char_handle_rx)
####################################



sensor_data = [[0 for _ in range(32)] for _ in range(32)]
row_mask=[19, 2, 17, 0, 23, 6, 21, 4, 27, 10, 25, 8, 31, 14, 29, 12, 13, 28, 15, 30, 9, 24, 11, 26, 5, 20, 7, 22, 1, 16, 3, 18]
col_mask=[3, 18, 1, 16, 7, 22, 5, 20, 11, 26, 9, 24, 15, 30, 13, 28, 29, 12, 31, 14, 25, 8, 27, 10, 21, 4, 23, 6, 17, 0, 19, 2]
#################################### 

##########MUX INITIALIZING##########
Pin_R0=Pin(12,mode=Pin.OUT,value=0)# rows
Pin_R1=Pin(13,mode=Pin.OUT,value=0)
Pin_R2=Pin(15,mode=Pin.OUT,value=0)
Pin_R3=Pin(27,mode=Pin.OUT,value=0)
Pin_R4=Pin(14,mode=Pin.OUT,value=0)
R_Pins = [Pin_R0, Pin_R1, Pin_R2, Pin_R3, Pin_R4]

Pin_C0=Pin(18,mode=Pin.OUT,value=0)# columns
Pin_C1=Pin(33,mode=Pin.OUT,value=0)
Pin_C2=Pin(25,mode=Pin.OUT,value=0)
Pin_C3=Pin(5, mode=Pin.OUT,value=0)
Pin_C4=Pin(17,mode=Pin.OUT,value=0)
C_Pins = [Pin_C0, Pin_C1, Pin_C2, Pin_C3, Pin_C4]  
####################################    


##########DAC INITIALIZING##########
Pin_DAC=Pin(26,Pin.OUT)
dac=DAC(Pin_DAC)
####################################

##########ADC INITIALIZING##########
Pin_sda=Pin(21,Pin.OUT)
Pin_scl=Pin(22,Pin.OUT)
i2c=I2C(1,scl=Pin_scl,sda=Pin_sda)
    
adc=ADS1115(i2c,0x48,1)
adc.set_conv(3,1,None)
####################################

Pin_HL_Switch=Pin(16,mode=Pin.OUT) #initialize pin controlling HL switch
Pin_HL_Switch.value(0) # 0 for low-freq, 1 for high-freq

def select(pins, index):
    for i in range(5):
        pins[i].value(index & (1<<i))
    
def scan():
    t = time.time()
    dac.write(95)
    for i in range(32):
        select(R_Pins, row_mask[i])
        for j in range(32):
            select(C_Pins, col_mask[j])
            #time.sleep(0.01)#stablize, this number could be adjusted
            value = adc.read_rev()
            sensor_data[i][j] = value
            #print(value)
            #print(i, j, adc.raw_to_v(value))

    dac.write(0)
    print(time.time()-t)

def list_to_str():
    sarr = 'str'
    for line in sensor_data:
        for i in line:
            sarr += str(i)
            sarr += '.'
    sarr += 'end'
    return sarr
   
def onepixel(vol, i, j):
    dac.write(vol)
    Pin_R0.value(i&1)#scan row
    Pin_R1.value(i&2)
    Pin_R2.value(i&4)
    Pin_R3.value(i&8)
    Pin_R4.value(i&16)
    
    Pin_C0.value(j&1)#scan column
    Pin_C1.value(j&2)
    Pin_C2.value(j&4)
    Pin_C3.value(j&8)
    Pin_C4.value(j&16)
    for x in range(10000):
        time.sleep_ms(1)
        value=adc.read_rev()
        print(value)

#onepixel(50,3,17)
while True:
    try:
        scan()
        send_data(list_to_str().encode('utf-8'))
    except Exception as e:
        print("出现异常:", e)
        time.sleep(1)

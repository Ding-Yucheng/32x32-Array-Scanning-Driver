from machine import Pin,DAC,I2C
from ads1x15 import ADS1114
import time
import usocket as socket
import esp
import network
'''
# Network setting
ssid = 'MyESP32'
password = '12345678'
host_ip = '192.168.137.232'
host_port = 54080

station = network.WLAN(network.STA_IF)
station.active(True)

while station.isconnected() == False:
    station.connect(ssid, password)
    pass

addr = socket.getaddrinfo(host_ip, host_port)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
conn, addr = s.accept()
print('listening on', addr)

print('Connection successful')
print(station.ifconfig())
'''
class MyMCU:
    row_mask=[19, 2, 17, 0, 23, 6, 21, 4, 27, 10, 25, 8, 31, 14, 29, 12, 13, 28, 15, 30, 9, 24, 11, 26, 5, 20, 7, 22, 1, 16, 3, 18]
    col_mask=[3, 18, 1, 16, 7, 22, 5, 20, 11, 26, 9, 24, 15, 30, 13, 28, 29, 12, 31, 14, 25, 8, 27, 10, 21, 4, 23, 6, 17, 0, 19, 2]


    
Pin_R0=Pin(12,mode=Pin.OUT,value=0,)#initialize pins controlling rows
Pin_R1=Pin(13,mode=Pin.OUT,value=0)
Pin_R2=Pin(15,mode=Pin.OUT,value=0)
Pin_R3=Pin(27,mode=Pin.OUT,value=0)
Pin_R4=Pin(14,mode=Pin.OUT,value=0)
    
Pin_C0=Pin(18,mode=Pin.OUT,value=0)#initialize pins controlling columns
Pin_C1=Pin(33,mode=Pin.OUT,value=0)
Pin_C2=Pin(25,mode=Pin.OUT,value=0)
Pin_C3=Pin(5, mode=Pin.OUT,value=0)
Pin_C4=Pin(17,mode=Pin.OUT,value=0)
    
Pin_HL_Switch=Pin(16,mode=Pin.OUT)#initialize pin controlling HL switch
    
Pin_DAC=Pin(26,Pin.OUT)#initialize dac
dac=DAC(Pin_DAC)
    
Pin_sda=Pin(21,Pin.OUT)#initialize i2c interface communicating with adc
Pin_scl=Pin(22,Pin.OUT)
i2c=I2C(1,scl=Pin_scl,sda=Pin_sda)
    
adc=ADS1114(i2c,0x48,2)
    
Pin_HL_Switch.value(0)

def scan():

    dac.write(95)
    for i in MyMCU.row_mask:
        Pin_R0.value(i&1)#scan row
        Pin_R1.value(i&2)
        Pin_R2.value(i&4)
        Pin_R3.value(i&8)
        Pin_R4.value(i&16)
        for j in MyMCU.col_mask:
            Pin_C0.value(j&1)#scan column
            Pin_C1.value(j&2)
            Pin_C2.value(j&4)
            Pin_C3.value(j&8)
            Pin_C4.value(j&16)
            
            time.sleep(0.01)#stablize, this number could be adjusted
            
            value=adc.read()
            print(hex(value))
            #print(adc.raw_to_v(value))

    dac.write(0)
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
        time.sleep(0.1)#stablize, this number could be adjusted
            
        value=adc.read()
        print(value)
#scan()   
onepixel(95,10,10)
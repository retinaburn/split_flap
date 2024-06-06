import machine
from machine import Pin
import time

#hs_1 = machine.ADC(27)
hs_2 = machine.ADC(26)
#he = Pin(26, Pin.IN)

while True:
        value = hs_2.read_u16()
        
        #print(f"1: {hs_1.read_u16()}, 2: {hs_2.read_u16()}")
        if value <= 4000:
            found = True
        else:
            found = False
        print(f"2: {value}, {found}")
        time.sleep(0.5)
        
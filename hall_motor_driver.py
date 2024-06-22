#Source: electrocredible.com, Language: MicroPython
from machine import Pin
import machine
import random
import time
import asyncio

DETECT_LEVEL = 5000  #Level below shows magnet detected

hall_sensor1 = machine.ADC(27)
hall_sensor2 = machine.ADC(26)

AT = 0
NEXT = 1
DETECTED = 2
motor1 = [None] * 3
motor1[AT] = -1
motor1[NEXT] = -1
motor1[DETECTED] = False

async def sensor_loop():
    global motor1
    while True:
            value1 = hall_sensor1.read_u16()
            detected1 = value1 < DETECT_LEVEL            
            motor1[DETECTED] = detected1
            
            value2 = hall_sensor2.read_u16()
            detected2 = value2 < DETECT_LEVEL
            
            #print(f"Value: {value1}, {detected1}, {value2}, {detected2}")
            
            
            await asyncio.sleep(0.01)
        
# Define the pins for the stepper motor
stepper_pins1 = [Pin(16, Pin.OUT), Pin(17, Pin.OUT), Pin(14, Pin.OUT), Pin(15, Pin.OUT)]
stepper_pins2 = [Pin(10, Pin.OUT), Pin(11, Pin.OUT), Pin(12, Pin.OUT), Pin(13, Pin.OUT)]

# Define the sequence of steps for the motor to take
step_sequence = [
    [1, 0, 0, 1],
    [1, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 1],
]

async def step(motor, direction, steps, delay):
    # Use the global step_index variable so that it can be modified by this function
    global step_index
    # Loop through the specified number of steps in the specified direction
    for i in range(steps):
        # Add the specified direction to the current step index to get the new step index
        step_index = (step_index + direction) % len(step_sequence)
        # Loop through each pin in the motor
        for pin_index in range(len(stepper_pins1)):
            # Get the value for this pin from the step sequence using the current step index
            pin_value = step_sequence[step_index][pin_index] 
            # Set the pin to this value
            motor[pin_index].value(pin_value)
        # Delay for the specified amount of time before taking the next step
        await asyncio.sleep(delay)
# Set the initial step index to 0
step_index = 0

async def run_loop():
    global motor1
    while True:
        if (motor1[AT] == -1):
            print(f"motor1 AT: {motor1[AT]}, DETECTED: {motor1[DETECTED]}")
            while motor1[DETECTED] == False:
                print("seek STEP motor1 by 1")
                await step(stepper_pins1, 1, 204.8 * 1, 0.002)
            motor1[AT] = 0
            print(f"motor1 AT: {motor1[AT]}, DETECTED: {motor1[DETECTED]}")
        if motor1[AT] != motor1[NEXT]:
            print(f"next STEP motor1 by 1, {motor1[AT]} vs {motor1[NEXT]}")
            await step(stepper_pins1, 1, 204.8 * 1, 0.002)
            motor1[AT] += 1
            motor1[AT] = motor1[AT] % 10        
        await asyncio.sleep(0.01)

async def num_loop():
    global motor1
    while True:
        #print(f"At: {motor1[AT]}, NEXT: {motor1[NEXT]}")
        if motor1[AT] == motor1[NEXT]:
            print("FOUND!")
            await asyncio.sleep(1) 
            motor1[NEXT] = random.randint(0,9)
            print(f"Motor1 seeking to {motor1[NEXT]}")
        await asyncio.sleep(0.1)

motor1[NEXT] = 0

# Take the specified number of steps in the anti-clockwise direction with a delay of 0.01 seconds between steps
#asyncio.create_task(step(stepper_pins1, 1, 204.8 * 10, 0.002))
#asyncio.create_task(step(stepper_pins2, 1, 204.8 * 4, 0.002))
asyncio.create_task(run_loop())
asyncio.create_task(sensor_loop())
asyncio.create_task(num_loop())
# Take the specified number of steps in the clockwise direction with a delay of 0.01 seconds between steps
#step(-1, 1000, 0.001)

loop = asyncio.get_event_loop()
try:
    loop.run_forever()
except KeyboardInterrupt:
    loop.close()
print("Done")


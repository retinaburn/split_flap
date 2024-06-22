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
STEP_INDEX = 3

motor1 = [None] * 4
motor1[AT] = -1
motor1[NEXT] = -1
motor1[DETECTED] = False
motor1[STEP_INDEX] = 0

motor2 = [None] * 4
motor2[AT] = -1
motor2[NEXT] = -1
motor2[DETECTED] = False
motor2[STEP_INDEX] = 0

async def sensor_loop():
    global motor1, motor2
    while True:
            value1 = hall_sensor1.read_u16()
            detected1 = value1 < DETECT_LEVEL            
            motor1[DETECTED] = detected1
            
            value2 = hall_sensor2.read_u16()
            detected2 = value2 < DETECT_LEVEL
            motor2[DETECTED] = detected2
            
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

async def step(motor, direction, steps, delay, motor_number):
    # Use the global step_index variable so that it can be modified by this function
    global motor1, motor2
    # Loop through the specified number of steps in the specified direction
    for i in range(steps):
        # Add the specified direction to the current step index to get the new step index
        if (motor_number == 1):
            step_index = motor1[STEP_INDEX] = (motor1[STEP_INDEX] + direction) % len(step_sequence)
        if (motor_number == 2):
            step_index = motor2[STEP_INDEX] = (motor2[STEP_INDEX] + direction) % len(step_sequence)
        # Loop through each pin in the motor
        for pin_index in range(len(stepper_pins1)):
            # Get the value for this pin from the step sequence using the current step index
            pin_value = step_sequence[step_index][pin_index] 
            # Set the pin to this value
            motor[pin_index].value(pin_value)
        # Delay for the specified amount of time before taking the next step
        await asyncio.sleep(delay)
# Set the initial step index to 0
#step_index = 0

MOTOR1_FACTOR = 204.8

async def run_loop_motor1():
    global motor1
    while True:
        if (motor1[AT] == -1):
            print(f"motor1 AT: {motor1[AT]}, DETECTED: {motor1[DETECTED]}")
            while motor1[DETECTED] == False:
                print("seek STEP motor1 by 1")
                await step(stepper_pins1, 1, MOTOR1_FACTOR * 1, 0.002, 1)
            motor1[AT] = 0
            print(f"motor1 AT: {motor1[AT]}, DETECTED: {motor1[DETECTED]}")
        if motor1[AT] != motor1[NEXT]:
            print(f"next STEP motor1 by 1, {motor1[AT]} vs {motor1[NEXT]}")
            await step(stepper_pins1, 1, MOTOR1_FACTOR * 1, 0.002, 1)
            motor1[AT] += 1
            motor1[AT] = motor1[AT] % 10
        await asyncio.sleep(0.01)

MOTOR2_FACTOR = MOTOR1_FACTOR
MODE = 3

async def run_loop_motor2():
    global motor2
    while True:
        if (motor2[AT] == -1):
            print(f"motor2 AT: {motor2[AT]}, DETECTED: {motor2[DETECTED]}")
            while motor2[DETECTED] == False:
                print("seek STEP motor2 by 1")
                await step(stepper_pins2, 1, MOTOR2_FACTOR * 1, 0.002, 2)
            motor2[AT] = 0
            print(f"motor2 AT: {motor2[AT]}, DETECTED: {motor2[DETECTED]}")
        if motor2[AT] != motor2[NEXT]:
            print(f"next STEP motor2 by 1, {motor2[AT]} vs {motor2[NEXT]}")
            await step(stepper_pins2, 1, MOTOR2_FACTOR * 1, 0.002, 2)
            motor2[AT] += 1
            motor2[AT] = motor2[AT] % 10        
        await asyncio.sleep(0.01)

async def num_loop():
    global motor1, motor2
    while True:
        #print(f"At: {motor1[AT]}, NEXT: {motor1[NEXT]}")
        # if motor1[AT] == motor1[NEXT]:            
        #     print("MOTOR1 FOUND!")
        # if motor2[AT] == motor2[NEXT]:
        #     print("MOTOR2 FOUND!")
        print(f"{motor1[AT]} vs {motor1[NEXT]}, {motor2[AT]} vs {motor2[NEXT]}")            
        mode1 = motor1[AT] == motor1[NEXT]
        mode2 = motor2[AT] == motor2[NEXT]
        mode3 = motor1[AT] == motor1[NEXT] and motor2[AT] == motor2[NEXT]

        mode_test = False
        if MODE == 1:
            mode_test = mode1
        elif MODE == 2:
            mode_test = mode2
        elif MODE == 3:
            mode_test = mode3

        if mode_test == True:        
            await asyncio.sleep(5) 
            motor1[NEXT] = random.randint(0,9)
            print(f"Motor1 seeking to {motor1[NEXT]}")
            motor2[NEXT] = random.randint(0,9)
            print(f"Motor2 seeking to {motor2[NEXT]}")
        await asyncio.sleep(0.1)

motor1[NEXT] = 0
motor2[NEXT] = 0



if (MODE == 1 or MODE == 3):
    asyncio.create_task(run_loop_motor1())
if (MODE == 2 or MODE == 3):
    asyncio.create_task(run_loop_motor2())
asyncio.create_task(sensor_loop())
asyncio.create_task(num_loop())

loop = asyncio.get_event_loop()
try:
    loop.run_forever()
except KeyboardInterrupt:
    loop.close()
print("Done")


#Source: electrocredible.com, Language: MicroPython
from machine import Pin
import machine
import time
import asyncio

DETECT_LEVEL = 1800  #Level above shows magnet detected
NOISE_LEVEL = 3000
hall_sensor = machine.ADC(machine.Pin(26, machine.Pin.PULL_UP))

async def sensor_loop():
    
    while True:
            value = hall_sensor.read_u16()
            detected = value > DETECT_LEVEL and value < NOISE_LEVEL
            if (detected == True):
                print(f"Value: {value}, {detected}")
            
            await asyncio.sleep(0.050)
        
# Define the pins for the stepper motor
#stepper_pins = [Pin(16, Pin.OUT), Pin(17, Pin.OUT), Pin(14, Pin.OUT), Pin(15, Pin.OUT)]
stepper_pins = [Pin(10, Pin.OUT), Pin(11, Pin.OUT), Pin(12, Pin.OUT), Pin(13, Pin.OUT)]

# Define the sequence of steps for the motor to take
step_sequence = [
    [1, 0, 0, 1],
    [1, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 1],
]


async def step(direction, steps, delay):
    # Use the global step_index variable so that it can be modified by this function
    global step_index
    # Loop through the specified number of steps in the specified direction
    for i in range(steps):
        # Add the specified direction to the current step index to get the new step index
        step_index = (step_index + direction) % len(step_sequence)
        # Loop through each pin in the motor
        for pin_index in range(len(stepper_pins)):
            # Get the value for this pin from the step sequence using the current step index
            pin_value = step_sequence[step_index][pin_index] 
            # Set the pin to this value
            stepper_pins[pin_index].value(pin_value)
        # Delay for the specified amount of time before taking the next step
        await asyncio.sleep(delay)
# Set the initial step index to 0
step_index = 0
# Take the specified number of steps in the anti-clockwise direction with a delay of 0.01 seconds between steps
MOTOR_FACTOR=51.2
#for i in range(40):
    #step(1, 1.0 * MOTOR_FACTOR, 0.020)
    #step(1, 1.0 * MOTOR_FACTOR, 0.002)

# Set the initial step index to 0
step_index = 0
# Take the specified number of steps in the anti-clockwise direction with a delay of 0.01 seconds between steps
asyncio.create_task(step(1, 120 * MOTOR_FACTOR, 0.002))
asyncio.create_task(sensor_loop())
# Take the specified number of steps in the clockwise direction with a delay of 0.01 seconds between steps
#step(-1, 1000, 0.001)

loop = asyncio.get_event_loop()
try:
    loop.run_forever()
except KeyboardInterrupt:
    loop.close()
print("Done")

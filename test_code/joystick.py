import pygame
import serial
import time

# Setup serial (adjust port as needed)
ser = serial.Serial('COM5', 115200, timeout=1)
time.sleep(2)

# Initialize Pygame + controller
pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

# Acceleration smoothing
def apply_acceleration(value, prev, max_speed=1000, accel_rate=30):
    target = value * max_speed
    delta = target - prev
    delta = max(min(delta, accel_rate), -accel_rate)
    return prev + delta

# Axis values
x_speed = 0
y_speed = 0

# Sensitivity (scale joystick differently for each axis if needed)
x_sensitivity = 0.5  # X-axis (e.g. pan)
y_sensitivity = 0.5  # Y-axis (e.g. tilt)

# New: Fire flag
fire = 0

# Button mapping (change if different controller)
FIRE_BUTTON = 0  # e.g. A on Xbox

# Loop
try:
    while True:
        pygame.event.pump()
        raw_x = -joystick.get_axis(0)
        raw_y = -joystick.get_axis(1)  # Invert for natural up/down

        # Fire button
        fire = joystick.get_button(FIRE_BUTTON)

        # Deadzone
        deadzone = 0.1
        raw_x = 0 if abs(raw_x) < deadzone else raw_x
        raw_y = 0 if abs(raw_y) < deadzone else raw_y

        # Acceleration
        x_speed = apply_acceleration(raw_x * x_sensitivity, x_speed)
        y_speed = apply_acceleration(raw_y * y_sensitivity, y_speed)

        # Send to Arduino
        command = f"{int(x_speed)},{int(y_speed)},{int(fire)}\n"
        ser.write(command.encode('utf-8'))

        print(f"X: {x_speed}, Y: {y_speed}, Fire: {fire}")

        time.sleep(0.01)  # ~50Hz loop
except KeyboardInterrupt:
    print("Exiting...")
    ser.close()
    pygame.quit()

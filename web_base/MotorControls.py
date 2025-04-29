import serial
from utils import SharedData
import asyncio


class MotorControl:
    def __init__(self, port='/dev/ttyACM0', baudrate=115200, timeout=1):
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        self.x_speed = 0
        self.y_speed = 0
        self.fire = 0

        self.deadzone = 0.1  # Deadzone for joystick
        self.accel_rate = 20
        self.max_speed = 1000

        self.x_sensitivity = 1  # X-axis (e.g. pan)
        self.y_sensitivity = 0.1  # Y-axis (e.g. tilt)

    def apply_acceleration(self, value, prev, max_speed=1000, accel_rate=30):
        target = value * max_speed
        delta = target - prev
        delta = max(min(delta, accel_rate), -accel_rate)
        return prev + delta
    
    def invert_control(self, invert_x=False, invert_y=False):
        if invert_x:
            self.x_sensitivity = -abs(self.x_sensitivity)
        else:
            self.x_sensitivity = abs(self.x_sensitivity)

        if invert_y:
            self.y_sensitivity = -abs(self.y_sensitivity)
        else:
            self.y_sensitivity = abs(self.y_sensitivity)
    
    async def handle(self, shared_data: SharedData):
        while True:
            # Read shared data
            raw_x = shared_data.x_axe
            raw_y = shared_data.y_axe
            fire = shared_data.fire

            # Apply deadzone
            raw_x = 0 if abs(raw_x) < self.deadzone else raw_x
            raw_y = 0 if abs(raw_y) < self.deadzone else raw_y

            # Apply acceleration
            self.x_speed = self.apply_acceleration(raw_x * self.x_sensitivity, self.x_speed, self.max_speed, self.accel_rate)
            self.y_speed = self.apply_acceleration(raw_y * self.y_sensitivity, self.y_speed, self.max_speed, self.accel_rate)

            # Scale and send to serial
            command = f"{self.x_speed},{self.y_speed},{int(fire)}\n"
            self.ser.write(command.encode('utf-8'))
            print(f"X: {self.x_speed}, Y: {self.y_speed}, Fire: {fire}")
            await asyncio.sleep(0.002)

        
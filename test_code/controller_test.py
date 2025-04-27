import pyrealsense2 as rs

# Create a pipeline
pipeline = rs.pipeline()

# Create a default config (NO manual stream configuration)
config = rs.config()

# Start pipeline without specifying any streams manually
pipeline.start()

try:
    while True:
        # Wait for the next available frames
        frames = pipeline.wait_for_frames()

        # Try to get IMU data
        accel_frame = frames.first_or_default(rs.stream.accel)
        gyro_frame = frames.first_or_default(rs.stream.gyro)

        if accel_frame:
            accel_data = accel_frame.as_motion_frame().get_motion_data()
            print(f"Accel: x={accel_data.x:.5f}, y={accel_data.y:.5f}, z={accel_data.z:.5f}")

        if gyro_frame:
            gyro_data = gyro_frame.as_motion_frame().get_motion_data()
            print(f"Gyro: x={gyro_data.x:.5f}, y={gyro_data.y:.5f}, z={gyro_data.z:.5f}")

except KeyboardInterrupt:
    print("Stopping pipeline...")

finally:
    pipeline.stop()


# # import usb.core
# # import usb.util

# # # Find the USB device (you need to know the Vendor ID and Product ID)
# # VID = 0x0738  # Mad Catz Vendor ID (replace with your device's Vendor ID)
# # PID = 0x1302  # Mad Catz Product ID (replace with your device's Product ID)

# # # Find the device
# # dev = usb.core.find(idVendor=VID, idProduct=PID)

# # if dev is None:
# #     raise ValueError('Device not found')

# # # Set the active configuration
# # dev.set_configuration()

# # # Print the device information
# # print(f"Device: {dev}")
# # print(f"Device Manufacturer: {usb.util.get_string(dev, 256, dev.iManufacturer)}")
# # print(f"Device Product: {usb.util.get_string(dev, 256, dev.iProduct)}")

# # Interact with the device (read/write data depending on your device's protocol)
# # For example, reading or sending control transfers:
# # You can refer to pyusb documentation on how to interact with the device

# # Example: control transfer to read data (adjust as needed)
# # response = dev.ctrl_transfer(0xC0, 0x01, 0, 0, 8)
# # print(response)


# import pygame
# import time

# # Initialize Pygame
# pygame.init()

# # Initialize the joystick
# pygame.joystick.init()

# # Check for joystick
# if pygame.joystick.get_count() == 0:
#     print("No joystick connected")
# else:
#     joystick = pygame.joystick.Joystick(0)
#     joystick.init()
#     print(f"Joystick name: {joystick.get_name()}")
#     print(f"Joystick ID: {joystick.get_id()}")

#     try:
#         while True:
#             # Process Pygame events
#             pygame.event.pump()

#             # Get axis values
#             axes = [joystick.get_axis(i) for i in range(joystick.get_numaxes())]
#             print(f"Axes: {axes}")

#             # Get button values
#             buttons = [joystick.get_button(i) for i in range(joystick.get_numbuttons())]
#             print(f"Buttons: {buttons}")

#             # Get hat values
#             hats = [joystick.get_hat(i) for i in range(joystick.get_numhats())]
#             print(f"Hats: {hats}")

#             # Wait for a short period to avoid flooding the console
#             time.sleep(1)

#     except KeyboardInterrupt:
#         print("Exiting...")

# # Quit Pygame
# pygame.quit()
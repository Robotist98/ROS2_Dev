# jetson_ws_realsense.py
import asyncio
import websockets
import pyrealsense2 as rs
import numpy as np
import cv2
import base64
import json
import time 
import serial 


#ser = serial.Serial('COM5', 115200, timeout=1)
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)  # Adjust the port as needed
time.sleep(2)

video = False

def apply_acceleration(value, prev, max_speed=1000, accel_rate=30):
    target = value * max_speed
    delta = target - prev
    delta = max(min(delta, accel_rate), -accel_rate)
    return prev + delta

async def handle_client(websocket, path):
    print("Client connected")

    # RealSense camera setup
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    pipeline.start(config)

    align = rs.align(rs.stream.color)

    # Axis values
    x_speed = 0
    y_speed = 0
    # Sensitivity (scale joystick differently for each axis if needed)
    x_sensitivity = 1  # X-axis (e.g. pan)
    y_sensitivity = 0.5  # Y-axis (e.g. tilt)

    deadzone = 0.1  # Deadzone for joystick
    fire = 0  # Fire flag

    try:
        while True:
            if video:
            # Get video frame from RealSense
                frames = pipeline.wait_for_frames()

                align_frames = align.process(frames)  # Align depth to color
                
                color_frame = align_frames.get_color_frame()
                depth_frame = align_frames.get_depth_frame()

                if not color_frame or not depth_frame:
                    continue

                color_frame_np = np.asanyarray(color_frame.get_data())
                _, jpeg_color = cv2.imencode('.jpg', color_frame_np)
                b64_frame = base64.b64encode(jpeg_color.tobytes()).decode('utf-8')

                color_depth_frame_np = cv2.applyColorMap(cv2.convertScaleAbs(np.asanyarray(depth_frame.get_data()), alpha=0.03), cv2.COLORMAP_JET)
                _, jpeg_depth = cv2.imencode('.jpg', color_depth_frame_np)
                b64_depth = base64.b64encode(jpeg_depth.tobytes()).decode('utf-8')

                # Send both color and depth frames in a single message
                await websocket.send(json.dumps({
                    "type": "frames",
                    "color": b64_frame,
                    "depth": b64_depth
                }))

            # Try to receive controller input with timeout
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=0.001)
                data = json.loads(message)
                if data.get("type") == "control":

                    raw_x = -data["axes"][0]  # X-axis
                    raw_y = -data["axes"][1]  # Y-axis
                    #print("Received controller input:", data)

                    raw_x = 0 if abs(raw_x) < deadzone else raw_x
                    raw_y = 0 if abs(raw_y) < deadzone else raw_y

                    # Apply deadzone
                    x_speed = apply_acceleration(raw_x * x_sensitivity, x_speed)
                    y_speed = apply_acceleration(raw_y * y_sensitivity, y_speed)

                    # Scale and send to serial
                    command = f"{x_speed},{y_speed},{int(fire)}\n"
                    ser.write(command.encode('utf-8'))  # Send to serial
                    print(f"X: {x_speed}, Y: {y_speed}, Fire: {fire}")

                    
                   
            except asyncio.TimeoutError:
                pass  # No control data this frame — just skip

            await asyncio.sleep(0.01)  # 100 FPS max output rate (tweak as needed)

    except websockets.ConnectionClosed:
        print("Client disconnected")
    finally:
        pipeline.stop()

# Start WebSocket server
async def main():
    print("Starting WebSocket server on ws://0.0.0.0:8765")
    async with websockets.serve(handle_client, '0.0.0.0', 8765):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())



# # jetson_ws_realsense.py
# import asyncio
# import websockets
# import pyrealsense2 as rs
# import numpy as np
# import cv2
# import base64
# import json

# async def handle_client(websocket, path):
#     pipeline = rs.pipeline()
#     config = rs.config()
#     config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
#     pipeline.start(config)

#     try:
#         while True:
#             frames = pipeline.wait_for_frames()
#             color_frame = frames.get_color_frame()
#             if not color_frame:
#                 continue

#             frame = np.asanyarray(color_frame.get_data())
#             _, jpeg = cv2.imencode('.jpg', frame)
#             b64_frame = base64.b64encode(jpeg.tobytes()).decode('utf-8')

#             # Send video frame
#             await websocket.send(json.dumps({"type": "video", "data": b64_frame}))

#             # Try to receive controller data
#             try:
#                 message = await asyncio.wait_for(websocket.recv(), timeout=0.01)
#                 data = json.loads(message)
#                 if data.get("type") == "control":
#                     print("Received controller input:", data)
#             except asyncio.TimeoutError:
#                 pass

#             await asyncio.sleep(0.033)
#     except websockets.ConnectionClosed:
#         print("Client disconnected.")
#     finally:
#         pipeline.stop()

# start_server = websockets.serve(handle_client, '0.0.0.0', 8765)
# print("WebSocket server started on port 8765")
# asyncio.get_event_loop().run_until_complete(start_server)
# asyncio.get_event_loop().run_forever()


# # server_receive.py
# import socket
# import pickle

# port = 5005

# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock.bind(('', port))

# print(f"Listening for controller data on port {port}...")

# while True:
#     data, addr = sock.recvfrom(4096)
#     controller_input = pickle.loads(data)
#     print("Received:", controller_input)

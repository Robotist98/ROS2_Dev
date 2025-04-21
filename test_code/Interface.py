import pygame
import serial
import time
import pyrealsense2 as rs
import cv2
from flask import Flask, Response
import numpy as np
from ultralytics import YOLO

# Setup serial (adjust port as needed)
try:
    ser = serial.Serial('COM5', 115200, timeout=1)
    time.sleep(2)
    serial_connected = True
except serial.SerialException:
    print("Warning: Could not connect to COM5. Continuing without serial communication.")
    ser = None
    serial_connected = False

# Initialize Pygame + controller
pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

# Flask app for video streaming
app = Flask(__name__)

# RealSense camera setup
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)

model = YOLO('yolov8n.pt')  # Load your YOLOv8 model




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

# Flask route for video streaming
def generate_frames():
    while True:
        try:
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            if not color_frame:
                continue
            frame = np.asanyarray(color_frame.get_data())

            # Run YOLO model on the frame
            results = model(frame)
            # Process results (e.g., draw boxes, labels, etc.)
            for result in results:
                boxes = result.boxes.xyxy  # Get bounding boxes
                for box in boxes:
                    x1, y1, x2, y2 = map(int, box[:4])  # Extract bounding box coordinates
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                    # Check if additional metadata (e.g., class ID) exists
                    if len(box) > 4:
                        class_id = int(box[4])  # Adjust index based on your model's output
                        cv2.putText(frame, f'ID: {class_id}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except Exception as e:
            print(f"Error in generate_frames: {e}")
            break

@app.route('/')
def index():
    return """
    <h1>Welcome to the Video Stream</h1>
    <p>Click <a href="/video_feed">here</a> to view the video feed.</p>
    """

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Loop
try:
    import threading
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)).start()

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

        # Send to Arduino (if serial is connected)
        if serial_connected:
            command = f"{int(x_speed)},{int(y_speed)},{int(fire)}\n"
            ser.write(command.encode('utf-8'))

        #print(f"X: {x_speed}, Y: {y_speed}, Fire: {fire}")

        time.sleep(0.01)  # ~50Hz loop
except KeyboardInterrupt:
    print("Exiting...")
    if serial_connected:
        ser.close()
    pygame.quit()
    pipeline.stop()
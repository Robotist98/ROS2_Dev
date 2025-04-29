
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from MotorControls import MotorControl
from utils import SharedData
import uvicorn
import json
import socket
import pyrealsense2 as rs
import cv2
import base64
import numpy as np
import asyncio

app = FastAPI()
shared_data = SharedData()
motor_control = MotorControl(port='/dev/ttyACM0', baudrate=115200, timeout=1)
motor_control.invert_control(invert_x=True, invert_y=True)

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Gamepad and Camera WebSocket</title>
</head>
<body>
    <h1>Gamepad and Camera WebSocket</h1>
    <p id="status">Connecting...</p>
    <img id="camera-feed" alt="Camera Feed" style="max-width: 100%; height: auto; border: 1px solid black;"/>

    <script>
        let socket;
        let gamepadIndex = null;
        let lastSentState = "";

        function connectWebSocket() {
            socket = new WebSocket(`ws://${location.host}/ws`);

            socket.addEventListener('open', () => {
                document.getElementById('status').innerText = "WebSocket Connected!";
                console.log('WebSocket connected');
            });

            socket.addEventListener('close', () => {
                document.getElementById('status').innerText = "WebSocket Disconnected!";
                console.log('WebSocket disconnected');
            });

            socket.addEventListener('error', (error) => {
                console.error('WebSocket error:', error);
            });

            socket.addEventListener('message', (event) => {
                try {
                    const data = JSON.parse(event.data);
                    if (data.image) {
                        document.getElementById('camera-feed').src = `data:image/jpeg;base64,${data.image}`;
                    }
                } catch (err) {
                    console.error("WebSocket message parse error:", err);
                }
            });
        }

        window.addEventListener("gamepadconnected", (e) => {
            console.log("Gamepad connected:", e.gamepad.id);
            gamepadIndex = e.gamepad.index;
            pollGamepad();
        });

        function pollGamepad() {
            if (gamepadIndex !== null && socket.readyState === WebSocket.OPEN) {
                const gp = navigator.getGamepads()[gamepadIndex];
                if (gp) {
                    const payload = {
                        buttons: gp.buttons.map(b => b.pressed),
                        axes: gp.axes
                    };
                    const jsonPayload = JSON.stringify(payload);
                    if (jsonPayload !== lastSentState) {
                        socket.send(jsonPayload);
                        lastSentState = jsonPayload;
                    }
                }
            }
            setTimeout(pollGamepad, 5);  // 200Hz polling
        }

        connectWebSocket();
    </script>
</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket client connected!")


    async def receive_gamepad_data():
        while True:
            try:
                data = await websocket.receive_text()
                gamepad_data = json.loads(data)
                axes = [round(axis, 2) for axis in gamepad_data.get("axes", [])]
                buttons = gamepad_data.get("buttons", [])
                shared_data.x_axe = axes[0] if len(axes) > 0 else 0
                shared_data.y_axe = axes[1] if len(axes) > 1 else 0
                shared_data.fire = 1 if len(buttons) > 0 and buttons[0] else 0
                #print("Axes:", axes)
                #print("Buttons:", buttons)
                # Optionally process gamepad input here
            except Exception as e:
                print("Gamepad receive error:", e)
                break

    async def send_camera_frames():
        pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 60)
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 60)
        pipeline.start(config)
        align = rs.align(rs.stream.color)
        try:
            while True:
                try:
                    frames = pipeline.wait_for_frames()
                    align_frames = align.process(frames)  # Align depth to color
                    # Get color frame
                    color_frame = align_frames.get_color_frame()
                    if not color_frame:
                        continue
                    color_image = np.asanyarray(color_frame.get_data())
                    _, buffer = cv2.imencode('.jpg', color_image)
                    image_base64 = base64.b64encode(buffer).decode('utf-8')
                    await websocket.send_text(json.dumps({"image": image_base64}))
                    await asyncio.sleep(0.02)  # ~30 FPS
                except Exception as e:
                    print("Camera send error:", e)
                    break
        finally:
            pipeline.stop()

    try:
        receive_task = asyncio.create_task(receive_gamepad_data())
        camera_task = asyncio.create_task(send_camera_frames())
        motor_task = asyncio.create_task(motor_control.handle(shared_data))
        await asyncio.gather(receive_task, camera_task, motor_task)
    except Exception as e:
        print("WebSocket disconnected:", e)

if __name__ == "__main__":
    host = "0.0.0.0"
    port = 8000
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    print(f"Server running at http://{ip_address}:{port}")
    uvicorn.run(app, host=host, port=port)


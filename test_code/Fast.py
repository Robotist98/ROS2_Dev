from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
import cv2
import pyrealsense2 as rs
import numpy as np

app = FastAPI()

# Setup RealSense pipeline
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)

def gen_frames():
    try:
        while True:
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            if not color_frame:
                continue
            frame = np.asanyarray(color_frame.get_data())
            
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        pipeline.stop()

@app.get("/")
def index():
    return Response(content="""
        <html>
            <body>
                <h1>RealSense Live Stream</h1>
                <img src="/video" width="640" height="480"/>
            </body>
        </html>
    """, media_type="text/html")

@app.get("/video")
def video_feed():
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

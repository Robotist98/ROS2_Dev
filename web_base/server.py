from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import uvicorn
import json
import socket

app = FastAPI()

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Gamepad WebSocket Sender</title>
</head>
<body>
    <h1>Gamepad WebSocket Sender</h1>
    <p id="status">Connecting...</p>

    <script>
        let socket;
        let gamepadIndex = null;

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
        }

        window.addEventListener("gamepadconnected", (e) => {
            console.log("Gamepad connected at index %d: %s.", e.gamepad.index, e.gamepad.id);
            gamepadIndex = e.gamepad.index;
            pollGamepad();
        });

        function pollGamepad() {
            if (gamepadIndex !== null) {
                const gamepads = navigator.getGamepads();
                const gp = gamepads[gamepadIndex];
                if (gp && socket.readyState === WebSocket.OPEN) {
                    const payload = {
                        buttons: gp.buttons.map(button => button.pressed),
                        axes: gp.axes
                    };
                    socket.send(JSON.stringify(payload));
                }
            }
            requestAnimationFrame(pollGamepad);
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
    try:
        while True:
            data = await websocket.receive_text()
            gamepad_data = json.loads(data)
            #print("Received gamepad data:", gamepad_data)
            axes = gamepad_data.get("axes", [])
            buttons = gamepad_data.get("buttons", [])
            print("Axes:", axes)
            #print("Buttons:", buttons)
            # Process your gamepad data here
    except Exception as e:
        print("WebSocket disconnected:", e)

if __name__ == "__main__":
        host = "0.0.0.0"
        port = 8000
        ip_address = socket.gethostbyname(socket.gethostname())
        print(f"Server is running. Access it at: http://127.0.0.1:{port} or http://{ip_address}:{port}")
        uvicorn.run(app, host=host, port=port)
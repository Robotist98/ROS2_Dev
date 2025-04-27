# client_controller_stream.py
import asyncio
import websockets
import pygame
import cv2
import json
import numpy as np
import base64
import socket

# Adjustable parameters
CONTROL_SEND_RATE = 0.005  # 200 Hz
VIDEO_FRAME_TIMEOUT = 0.1  # seconds

# Controller sending loop
async def send_controls(ws, joystick):
    prev_axes = [0] * joystick.get_numaxes()
    prev_buttons = [0] * joystick.get_numbuttons()

    while True:
        pygame.event.pump()
        
        axes = [round(joystick.get_axis(i), 2) for i in range(joystick.get_numaxes())] if joystick.get_numaxes() > 0 else []
        buttons = [joystick.get_button(i) for i in range(joystick.get_numbuttons())]

        # Check for changes in axes or buttons
        axes_changed = [
            (axes[i] != prev_axes[i] and not (axes[i] == 0 and prev_axes[i] == 0))
            for i in range(len(axes))
        ]
        buttons_changed = [buttons[i] != prev_buttons[i] for i in range(len(buttons))]

        if any(axes_changed) or any(buttons_changed):
            control_data = {
                "type": "control",
                "axes": axes,
                "buttons": buttons
            }
            try:
                await ws.send(json.dumps(control_data))
                print(f"Successfully sent control data: {control_data}")
            except websockets.exceptions.ConnectionClosed as e:
                print(f"WebSocket connection closed: {e}")
                break
            except Exception as e:
                print(f"Error sending control data: {e}")
                break

            # Update previous states
            prev_axes = axes
            prev_buttons = buttons

        await asyncio.sleep(CONTROL_SEND_RATE)

# Video receiving loop
async def receive_video(ws):
    while True:
        try:
            msg = await asyncio.wait_for(ws.recv(), timeout=VIDEO_FRAME_TIMEOUT)
            msg = json.loads(msg)

            if msg.get("type") == "frames":
                color_jpg = base64.b64decode(msg["color"])
                color_img_array = np.frombuffer(color_jpg, dtype=np.uint8)
                color_frame = cv2.imdecode(color_img_array, cv2.IMREAD_COLOR)
                cv2.imshow("Jetson Stream", color_frame)

                depth_jpg = base64.b64decode(msg["depth"])
                depth_img_array = np.frombuffer(depth_jpg, dtype=np.uint8)
                depth_frame = cv2.imdecode(depth_img_array, cv2.IMREAD_UNCHANGED)
                cv2.imshow("Depth Stream", depth_frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except asyncio.TimeoutError:
            continue
        except Exception as e:
            print(f"Error receiving video: {e}")
            break

def get_ip_from_hostname(hostname):
    try:
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except socket.error as e:
        return f"Error: {e}"

# Main function
async def main():

    hostname = "user-mobilerig"  # Replace with your hostname
    port = 8765  # Port for the WebSocket server
    ip_address = get_ip_from_hostname(hostname)
    uri = f"ws://{ip_address}:{port}"  # Replace if needed

    pygame.init()
    pygame.joystick.init()
    if pygame.joystick.get_count() == 0:
        print("No joystick detected!")
        return

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    print(f"Using joystick: {joystick.get_name()}")

    async with websockets.connect(uri) as ws:
        await asyncio.gather(
            send_controls(ws, joystick),
            receive_video(ws)
        )

if __name__ == "__main__":
    asyncio.run(main())


# # client_controller_stream.py
# import asyncio
# import websockets
# import pygame
# import cv2
# import json
# import numpy as np
# import base64

# async def main():
#     uri = "ws://10.42.0.1:8765"  # Replace if needed

#     # Init controller
#     pygame.init()
#     pygame.joystick.init()
#     joystick = pygame.joystick.Joystick(0)
#     joystick.init()

#     async with websockets.connect(uri) as ws:
#         while True:
#             # Read controller state
#             pygame.event.pump()
#             axes = [joystick.get_axis(i) for i in range(joystick.get_numaxes())]
#             buttons = [joystick.get_button(i) for i in range(joystick.get_numbuttons())]

#             control_data = {
#                 "type": "control",
#                 "axes": axes,
#                 "buttons": buttons
#             }
#             await ws.send(json.dumps(control_data))

#             # Receive and display video
#             try:
#                 msg = await asyncio.wait_for(ws.recv(), timeout=0.1)
#                 msg = json.loads(msg)
#                 if msg.get("type") == "video":
#                     jpg = base64.b64decode(msg["data"])
#                     img_array = np.frombuffer(jpg, dtype=np.uint8)
#                     frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
#                     cv2.imshow("Jetson Stream", frame)
#                     if cv2.waitKey(1) & 0xFF == ord('q'):
#                         break
#             except asyncio.TimeoutError:
#                 pass

# asyncio.run(main())


# import pygame
# import socket
# import pickle
# from time import sleep

# pygame.init()
# pygame.joystick.init()

# joystick = pygame.joystick.Joystick(0)
# joystick.init()

# server_ip = '10.42.0.1'
# port = 5005  # Make sure this port is not used by anything else

# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# def get_controller_input():
#     pygame.event.pump()
#     axes = [joystick.get_axis(i) for i in range(joystick.get_numaxes())]
#     buttons = [joystick.get_button(i) for i in range(joystick.get_numbuttons())]
#     return {'axes': axes, 'buttons': buttons}

# if __name__ == "__main__":

#     while True:
#         data = get_controller_input()
#         message = pickle.dumps(data)
#         sock.sendto(message, (server_ip, port))
#         sleep(0.05)  # 20 messages per second
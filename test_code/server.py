# server_receive.py
import socket
import pickle

port = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', port))

print(f"Listening for controller data on port {port}...")

while True:
    data, addr = sock.recvfrom(4096)
    controller_input = pickle.loads(data)
    print("Received:", controller_input)

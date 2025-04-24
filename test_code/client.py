import pygame
import socket
import pickle
from time import sleep

pygame.init()
pygame.joystick.init()

joystick = pygame.joystick.Joystick(0)
joystick.init()

server_ip = '192.168.1.42'
port = 5005  # Make sure this port is not used by anything else

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def get_controller_input():
    pygame.event.pump()
    axes = [joystick.get_axis(i) for i in range(joystick.get_numaxes())]
    buttons = [joystick.get_button(i) for i in range(joystick.get_numbuttons())]
    return {'axes': axes, 'buttons': buttons}

if __name__ == "__main__":

    while True:
        data = get_controller_input()
        message = pickle.dumps(data)
        sock.sendto(message, (server_ip, port))
        sleep(0.05)  # 20 messages per second
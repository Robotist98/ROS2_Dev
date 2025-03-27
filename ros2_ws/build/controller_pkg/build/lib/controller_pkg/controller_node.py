import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
import pygame

class ControllerNode(Node):
    def __init__(self):
        super().__init__('controller_node')
        self.publisher_ = self.create_publisher(Joy, 'joy', 10)
        self.timer = self.create_timer(0.1, self.timer_callback)  # 10 Hz

        # Initialize pygame
        pygame.init()
        pygame.joystick.init()
        try:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.get_logger().info('Joystick initialized successfully.')
        except pygame.error:
            self.joystick = None
            self.get_logger().error('No joystick connected.')

    def timer_callback(self):
        if self.joystick is None:
            self.get_logger().warn('No joystick connected.')
            return

        pygame.event.pump()
        axes = [self.joystick.get_axis(i) for i in range(self.joystick.get_numaxes())]
        buttons = [self.joystick.get_button(i) for i in range(self.joystick.get_numbuttons())]

        msg = Joy()
        msg.axes = axes
        msg.buttons = buttons
        self.publisher_.publish(msg)
        self.get_logger().info(f'Published Axes: {msg.axes}, Buttons: {msg.buttons}')

def main(args=None):
    rclpy.init(args=args)
    node = ControllerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
    pygame.quit()

if __name__ == '__main__':
    main()
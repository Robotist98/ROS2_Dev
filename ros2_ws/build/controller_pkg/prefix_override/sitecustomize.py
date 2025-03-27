import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/ROS2_Dev/ros2_ws/install/controller_pkg'

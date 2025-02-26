FROM osrf/ros:humble-desktop

# Add ubuntu user with same UID and GID as your host system
ARG USERNAME=ubuntu
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ARG REPOSITORY_NAME=$(pwd)

RUN if ! id -u $USER_UID >/dev/null 2>&1; then \
        groupadd --gid $USER_GID $USERNAME && \
        useradd -s /bin/bash --uid $USER_UID --gid $USER_GID -m $USERNAME; \
    fi
# Add sudo support for the non-root user
RUN apt-get update && \
    apt-get install -y sudo && \
    echo "$USERNAME ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME && \
    chmod 0440 /etc/sudoers.d/$USERNAME

# Switch from root to user
USER $USERNAME

# Add user to video group to allow access to webcam
RUN sudo usermod --append --groups video $USERNAME

RUN sudo apt-get update && \
    for i in {1..5}; do sudo apt-get upgrade -y --fix-missing && break || sleep 15; done

# Install Git
RUN sudo apt install -y git


# Install OpenGL and utilities for RViz
RUN sudo apt-get install -y \
    mesa-utils \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    x11-apps

# Install required Qt platform plugins
RUN sudo apt-get install -y \
    libxcb-xinerama0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xkb1 \
    libxkbcommon-x11-0

RUN sudo apt-get install -y \
    terminator \
    python3-pip \
    gedit

# Rosdep update
RUN rosdep update

RUN sudo apt-get install -y \
    python3-colcon-common-extensions

# Install gazebo 
RUN sudo apt-get install -y \
    ros-humble-gazebo-ros-pkgs

# Install Nav2
RUN sudo apt-get install -y \
    ros-${ROS_DISTRO}-navigation2 \
    ros-${ROS_DISTRO}-nav2-bringup

# Install rtabmap 
RUN sudo apt-get install -y \
    ros-${ROS_DISTRO}-rtabmap-ros


# Source the ROS setup file
RUN echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> ~/.bashrc
RUN echo "source /${REPOSITORY_NAME}/ros2_ws/install/setup.bash" >> ~/.bashrc
RUN echo "source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash" >> ~/.bashrc

ENV QT_X11_NO_MITSHM=1

# Ubuntu package manager dependencies
RUN sudo apt-get install -y \
    lsb-release \
    wget \
    gnupg

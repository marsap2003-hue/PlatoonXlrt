from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='platooning_pkg',
            executable='gazebo_master',
            name='gazebo_master',
            output='screen'
        ),
        Node(
            package='platooning_pkg',
            executable='gazebo_slave',
            name='gazebo_slave',
            output='screen'
        ),
        Node(
            package='platooning_pkg',
            executable='data_logger',
            name='data_logger',
            output='screen'
        ),
    ])

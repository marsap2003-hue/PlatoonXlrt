from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='platooning_pkg',
            executable='gazebo_leader',
            name='gazebo_leader',
            output='screen'
        ),
        Node(
            package='platooning_pkg',
            executable='gazebo_follower',
            name='gazebo_follower',
            output='screen'
        ),
        Node(
            package='platooning_pkg',
            executable='data_logger',
            name='data_logger',
            output='screen'
        ),
    ])

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    master = Node(
        package='platooning_pkg',
        executable='gazebo_circular_master',
        name='gazebo_circular_master',
        output='screen'
    )

    slave1 = Node(
        package='platooning_pkg',
        executable='gazebo_circular_slave',
        name='gazebo_circular_slave1',
        output='screen',
        parameters=[{
            'slave_id': 1,
            'predecessor_topic': '/gazebo_master_state',
            'state_topic': '/gazebo_slave1_state',
            'model_name': 'slave1_vehicle',
            'initial_s': -5.0
        }]
    )

    slave2 = Node(
        package='platooning_pkg',
        executable='gazebo_circular_slave',
        name='gazebo_circular_slave2',
        output='screen',
        parameters=[{
            'slave_id': 2,
            'predecessor_topic': '/gazebo_slave1_state',
            'state_topic': '/gazebo_slave2_state',
            'model_name': 'slave2_vehicle',
            'initial_s': -10.0
        }]
    )

    slave3 = Node(
        package='platooning_pkg',
        executable='gazebo_circular_slave',
        name='gazebo_circular_slave3',
        output='screen',
        parameters=[{
            'slave_id': 3,
            'predecessor_topic': '/gazebo_slave2_state',
            'state_topic': '/gazebo_slave3_state',
            'model_name': 'slave3_vehicle',
            'initial_s': -15.0
        }]
    )

    logger = Node(
        package='platooning_pkg',
        executable='gazebo_circular_logger',
        name='gazebo_circular_logger',
        output='screen'
    )

    return LaunchDescription([
        master,
        slave1,
        slave2,
        slave3,
        logger
    ])

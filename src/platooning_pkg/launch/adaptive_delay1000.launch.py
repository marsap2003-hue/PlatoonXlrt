from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    master = Node(
        package='platooning_pkg',
        executable='string_master_node',
        name='string_master',
        output='screen'
    )

    slave1 = Node(
        package='platooning_pkg',
        executable='adaptive_slave_node',
        name='adaptive_slave1',
        output='screen',
        parameters=[{
            'slave_id': 1,
            'predecessor_topic': '/master_state',
            'initial_position': -45.0,
            'communication_delay': 1.0,
            'base_headway': 1.0,
            'delay_gain': 1.0,
            'csv_name': 'slave1_adaptive_delay1000.csv'
        }]
    )

    slave2 = Node(
        package='platooning_pkg',
        executable='adaptive_slave_node',
        name='adaptive_slave2',
        output='screen',
        parameters=[{
            'slave_id': 2,
            'predecessor_topic': '/slave1_state',
            'initial_position': -90.0,
            'communication_delay': 1.0,
            'base_headway': 1.0,
            'delay_gain': 1.0,
            'csv_name': 'slave2_adaptive_delay1000.csv'
        }]
    )

    slave3 = Node(
        package='platooning_pkg',
        executable='adaptive_slave_node',
        name='adaptive_slave3',
        output='screen',
        parameters=[{
            'slave_id': 3,
            'predecessor_topic': '/slave2_state',
            'initial_position': -135.0,
            'communication_delay': 1.0,
            'base_headway': 1.0,
            'delay_gain': 1.0,
            'csv_name': 'slave3_adaptive_delay1000.csv'
        }]
    )

    return LaunchDescription([
        master,
        slave1,
        slave2,
        slave3
    ])

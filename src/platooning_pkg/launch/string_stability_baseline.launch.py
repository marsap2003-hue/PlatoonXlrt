from launch import LaunchDescription
from launch.actions import RegisterEventHandler, EmitEvent
from launch.event_handlers import OnProcessExit
from launch.events import Shutdown
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
        executable='multi_slave_node',
        name='slave1',
        output='screen',
        parameters=[{
            'slave_id': 1,
            'predecessor_topic': '/master_state',
            'initial_position': -25.0,
            'communication_delay': 0.0,
            'csv_name': 'slave1_string_baseline_new.csv'
        }]
    )

    slave2 = Node(
        package='platooning_pkg',
        executable='multi_slave_node',
        name='slave2',
        output='screen',
        parameters=[{
            'slave_id': 2,
            'predecessor_topic': '/slave1_state',
            'initial_position': -50.0,
            'communication_delay': 0.0,
            'csv_name': 'slave2_string_baseline_new.csv'
        }]
    )

    slave3 = Node(
        package='platooning_pkg',
        executable='multi_slave_node',
        name='slave3',
        output='screen',
        parameters=[{
            'slave_id': 3,
            'predecessor_topic': '/slave2_state',
            'initial_position': -75.0,
            'communication_delay': 0.0,
            'csv_name': 'slave3_string_baseline_new.csv'
        }]
    )

    # When the Master finishes, automatically shut down
    # the entire launch system, including all Slave nodes.
    shutdown_when_master_finishes = RegisterEventHandler(
        OnProcessExit(
            target_action=master,
            on_exit=[
                EmitEvent(
                    event=Shutdown(
                        reason='String-stability Master completed'
                    )
                )
            ]
        )
    )

    return LaunchDescription([
        master,
        slave1,
        slave2,
        slave3,
        shutdown_when_master_finishes
    ])

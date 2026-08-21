from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def launch_setup(context, *args, **kwargs):

    delay = float(
        LaunchConfiguration('delay').perform(context)
    )

    run_name = LaunchConfiguration(
        'run_name'
    ).perform(context)

    # Improved controller candidate
    headway = 1.25

    # d = d0 + h*v = 5 + 1.25*20 = 30 m
    initial_gap = 30.0

    master = Node(
        package='platooning_pkg',
        executable='string_master_node',
        name='string_master',
        output='screen'
    )

    slave1 = Node(
        package='platooning_pkg',
        executable='adaptive_slave_node',
        name='improved_slave1',
        output='screen',
        parameters=[{
            'slave_id': 1,
            'predecessor_topic': '/master_state',
            'initial_position': -initial_gap,
            'communication_delay': delay,
            'base_headway': headway,
            'delay_gain': 0.0,
            'csv_name': f'slave1_improved_{run_name}.csv'
        }]
    )

    slave2 = Node(
        package='platooning_pkg',
        executable='adaptive_slave_node',
        name='improved_slave2',
        output='screen',
        parameters=[{
            'slave_id': 2,
            'predecessor_topic': '/slave1_state',
            'initial_position': -2.0 * initial_gap,
            'communication_delay': delay,
            'base_headway': headway,
            'delay_gain': 0.0,
            'csv_name': f'slave2_improved_{run_name}.csv'
        }]
    )

    slave3 = Node(
        package='platooning_pkg',
        executable='adaptive_slave_node',
        name='improved_slave3',
        output='screen',
        parameters=[{
            'slave_id': 3,
            'predecessor_topic': '/slave2_state',
            'initial_position': -3.0 * initial_gap,
            'communication_delay': delay,
            'base_headway': headway,
            'delay_gain': 0.0,
            'csv_name': f'slave3_improved_{run_name}.csv'
        }]
    )

    return [
        master,
        slave1,
        slave2,
        slave3
    ]


def generate_launch_description():

    return LaunchDescription([

        DeclareLaunchArgument(
            'delay',
            default_value='0.0'
        ),

        DeclareLaunchArgument(
            'run_name',
            default_value='delay0'
        ),

        OpaqueFunction(
            function=launch_setup
        )
    ])

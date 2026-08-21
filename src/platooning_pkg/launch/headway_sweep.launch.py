from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def launch_setup(context, *args, **kwargs):

    headway = float(
        LaunchConfiguration('headway').perform(context)
    )

    run_name = LaunchConfiguration(
        'run_name'
    ).perform(context)

    # Desired initial spacing:
    # d = d0 + h*v = 5 + h*20
    initial_gap = 5.0 + headway * 20.0

    slave1_position = -initial_gap
    slave2_position = -2.0 * initial_gap
    slave3_position = -3.0 * initial_gap

    communication_delay = 1.0

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
            'initial_position': slave1_position,
            'communication_delay': communication_delay,

            # We directly select the tested headway
            'base_headway': headway,
            'delay_gain': 0.0,

            'csv_name':
                f'slave1_headway_{run_name}.csv'
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
            'initial_position': slave2_position,
            'communication_delay': communication_delay,
            'base_headway': headway,
            'delay_gain': 0.0,
            'csv_name':
                f'slave2_headway_{run_name}.csv'
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
            'initial_position': slave3_position,
            'communication_delay': communication_delay,
            'base_headway': headway,
            'delay_gain': 0.0,
            'csv_name':
                f'slave3_headway_{run_name}.csv'
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
            'headway',
            default_value='1.0'
        ),

        DeclareLaunchArgument(
            'run_name',
            default_value='h100'
        ),

        OpaqueFunction(
            function=launch_setup
        )
    ])

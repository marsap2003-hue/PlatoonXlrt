from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def launch_setup(context, *args, **kwargs):

    loss = float(
        LaunchConfiguration('loss').perform(context)
    )

    headway = float(
        LaunchConfiguration('headway').perform(context)
    )

    run_name = LaunchConfiguration(
        'run_name'
    ).perform(context)

    seed = int(
        LaunchConfiguration('seed').perform(context)
    )

    # Correct initial spacing for the selected headway
    initial_gap = 5.0 + headway * 20.0

    master = Node(
        package='platooning_pkg',
        executable='string_master_node',
        name='string_master',
        output='screen'
    )

    slave1 = Node(
        package='platooning_pkg',
        executable='multi_slave_packetloss',
        name='packetloss_slave1',
        output='screen',
        parameters=[{
            'slave_id': 1,
            'predecessor_topic': '/master_state',
            'initial_position': -initial_gap,
            'packet_loss_probability': loss,
            'headway': headway,
            'random_seed': seed,
            'csv_name': f'slave1_{run_name}.csv'
        }]
    )

    slave2 = Node(
        package='platooning_pkg',
        executable='multi_slave_packetloss',
        name='packetloss_slave2',
        output='screen',
        parameters=[{
            'slave_id': 2,
            'predecessor_topic': '/slave1_state',
            'initial_position': -2.0 * initial_gap,
            'packet_loss_probability': loss,
            'headway': headway,
            'random_seed': seed,
            'csv_name': f'slave2_{run_name}.csv'
        }]
    )

    slave3 = Node(
        package='platooning_pkg',
        executable='multi_slave_packetloss',
        name='packetloss_slave3',
        output='screen',
        parameters=[{
            'slave_id': 3,
            'predecessor_topic': '/slave2_state',
            'initial_position': -3.0 * initial_gap,
            'packet_loss_probability': loss,
            'headway': headway,
            'random_seed': seed,
            'csv_name': f'slave3_{run_name}.csv'
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
            'loss',
            default_value='0.0'
        ),

        DeclareLaunchArgument(
            'headway',
            default_value='1.0'
        ),

        DeclareLaunchArgument(
            'run_name',
            default_value='test'
        ),

        DeclareLaunchArgument(
            'seed',
            default_value='1'
        ),

        OpaqueFunction(
            function=launch_setup
        )
    ])

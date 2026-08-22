import csv
import os
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray


class GazeboCircularLogger(Node):

    def __init__(self):
        super().__init__('gazebo_circular_logger')

        self.start_time = time.time()
        self.desired_distance = 5.0

        # Latest states: [time, s, velocity]
        self.states = {
            'master': None,
            'slave1': None,
            'slave2': None,
            'slave3': None
        }

        self.create_subscription(
            Float64MultiArray,
            '/gazebo_master_state',
            lambda msg: self.state_callback('master', msg),
            10
        )

        self.create_subscription(
            Float64MultiArray,
            '/gazebo_slave1_state',
            lambda msg: self.state_callback('slave1', msg),
            10
        )

        self.create_subscription(
            Float64MultiArray,
            '/gazebo_slave2_state',
            lambda msg: self.state_callback('slave2', msg),
            10
        )

        self.create_subscription(
            Float64MultiArray,
            '/gazebo_slave3_state',
            lambda msg: self.state_callback('slave3', msg),
            10
        )

        # Save directly inside the package results directory.
        package_source = os.path.expanduser(
            '~/ros2_ws/src/platooning_pkg'
        )

        results_dir = os.path.join(
            package_source,
            'results',
            'gazebo_circular'
        )

        os.makedirs(
            results_dir,
            exist_ok=True
        )

        self.csv_path = os.path.join(
            results_dir,
            'gazebo_circular_platoon_data.csv'
        )

        self.csv_file = open(
            self.csv_path,
            'w',
            newline=''
        )

        self.writer = csv.writer(
            self.csv_file
        )

        self.writer.writerow([
            'time',
            'master_s',
            'slave1_s',
            'slave2_s',
            'slave3_s',
            'master_velocity',
            'slave1_velocity',
            'slave2_velocity',
            'slave3_velocity',
            'distance_master_slave1',
            'distance_slave1_slave2',
            'distance_slave2_slave3',
            'error_slave1',
            'error_slave2',
            'error_slave3'
        ])

        self.timer = self.create_timer(
            0.1,
            self.log_data
        )

        self.get_logger().info(
            f'Circular Gazebo logger started | '
            f'CSV: {self.csv_path}'
        )

    def state_callback(self, vehicle, msg):

        if len(msg.data) < 3:
            return

        self.states[vehicle] = [
            float(msg.data[0]),
            float(msg.data[1]),
            float(msg.data[2])
        ]

    def log_data(self):

        # Wait until all four vehicles have published.
        if any(
            state is None
            for state in self.states.values()
        ):
            return

        current_time = (
            time.time() -
            self.start_time
        )

        master = self.states['master']
        slave1 = self.states['slave1']
        slave2 = self.states['slave2']
        slave3 = self.states['slave3']

        master_s = master[1]
        slave1_s = slave1[1]
        slave2_s = slave2[1]
        slave3_s = slave3[1]

        master_v = master[2]
        slave1_v = slave1[2]
        slave2_v = slave2[2]
        slave3_v = slave3[2]

        distance1 = (
            master_s -
            slave1_s
        )

        distance2 = (
            slave1_s -
            slave2_s
        )

        distance3 = (
            slave2_s -
            slave3_s
        )

        error1 = (
            distance1 -
            self.desired_distance
        )

        error2 = (
            distance2 -
            self.desired_distance
        )

        error3 = (
            distance3 -
            self.desired_distance
        )

        self.writer.writerow([
            current_time,
            master_s,
            slave1_s,
            slave2_s,
            slave3_s,
            master_v,
            slave1_v,
            slave2_v,
            slave3_v,
            distance1,
            distance2,
            distance3,
            error1,
            error2,
            error3
        ])

        self.csv_file.flush()

        self.get_logger().info(
            f't={current_time:.1f} | '
            f'e1={error1:.3f} m | '
            f'e2={error2:.3f} m | '
            f'e3={error3:.3f} m'
        )

    def destroy_node(self):

        if not self.csv_file.closed:
            self.csv_file.close()

        super().destroy_node()


def main(args=None):

    rclpy.init(args=args)

    node = GazeboCircularLogger()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

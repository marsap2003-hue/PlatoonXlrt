import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

import csv
from collections import deque


class AdaptiveSlaveNode(Node):

    def __init__(self):
        super().__init__('adaptive_slave_node')

        self.declare_parameter('slave_id', 1)
        self.declare_parameter('predecessor_topic', '/master_state')
        self.declare_parameter('initial_position', -25.0)
        self.declare_parameter('csv_name', 'adaptive_slave.csv')
        self.declare_parameter('communication_delay', 0.0)

        # Adaptive-headway parameters
        self.declare_parameter('base_headway', 1.0)
        self.declare_parameter('delay_gain', 1.0)

        self.slave_id = int(
            self.get_parameter('slave_id').value
        )

        self.predecessor_topic = str(
            self.get_parameter('predecessor_topic').value
        )

        self.position = float(
            self.get_parameter('initial_position').value
        )

        self.csv_name = str(
            self.get_parameter('csv_name').value
        )

        self.communication_delay = float(
            self.get_parameter('communication_delay').value
        )

        self.base_headway = float(
            self.get_parameter('base_headway').value
        )

        self.delay_gain = float(
            self.get_parameter('delay_gain').value
        )

        # Communication-aware effective headway
        self.effective_headway = (
            self.base_headway +
            self.delay_gain * self.communication_delay
        )

        # Initial velocity
        self.velocity = 20.0

        # Same controller gains as original implementation
        self.kp = 0.5
        self.kv = 0.8
        self.d0 = 5.0
        self.dt = 0.1

        self.state_buffer = deque()

        self.state_topic = f'/slave{self.slave_id}_state'

        self.state_publisher = self.create_publisher(
            Float64MultiArray,
            self.state_topic,
            10
        )

        self.state_subscription = self.create_subscription(
            Float64MultiArray,
            self.predecessor_topic,
            self.predecessor_callback,
            10
        )

        self.csv_file = open(
            self.csv_name,
            'w',
            newline=''
        )

        self.csv_writer = csv.writer(self.csv_file)

        self.csv_writer.writerow([
            'control_time',
            'predecessor_state_time',
            'information_age',
            'slave_id',
            'communication_delay',
            'effective_headway',
            'predecessor_position',
            'slave_position',
            'predecessor_velocity',
            'slave_velocity',
            'actual_distance',
            'desired_distance',
            'distance_error',
            'velocity_error',
            'acceleration'
        ])

        self.get_logger().info(
            f'Adaptive Slave {self.slave_id} | '
            f'Delay: {self.communication_delay:.1f} s | '
            f'Headway: {self.effective_headway:.1f} s'
        )

    def predecessor_callback(self, msg):

        current_time = float(msg.data[0])
        predecessor_position = float(msg.data[1])
        predecessor_velocity = float(msg.data[2])

        self.state_buffer.append((
            current_time,
            predecessor_position,
            predecessor_velocity
        ))

        target_time = (
            current_time - self.communication_delay
        )

        if target_time < 0.0:
            return

        delayed_state = None

        while (
            len(self.state_buffer) > 0 and
            self.state_buffer[0][0] <= target_time + 1e-6
        ):
            delayed_state = self.state_buffer.popleft()

        if delayed_state is None:
            return

        predecessor_state_time = delayed_state[0]
        delayed_position = delayed_state[1]
        delayed_velocity = delayed_state[2]

        information_age = (
            current_time - predecessor_state_time
        )

        desired_distance = (
            self.d0 +
            self.effective_headway * self.velocity
        )

        actual_distance = (
            delayed_position -
            self.position
        )

        distance_error = (
            actual_distance -
            desired_distance
        )

        velocity_error = (
            delayed_velocity -
            self.velocity
        )

        acceleration = (
            self.kp * distance_error +
            self.kv * velocity_error
        )

        self.velocity += acceleration * self.dt
        self.position += self.velocity * self.dt

        state_msg = Float64MultiArray()

        state_msg.data = [
            current_time,
            self.position,
            self.velocity
        ]

        self.state_publisher.publish(state_msg)

        self.csv_writer.writerow([
            current_time,
            predecessor_state_time,
            information_age,
            self.slave_id,
            self.communication_delay,
            self.effective_headway,
            delayed_position,
            self.position,
            delayed_velocity,
            self.velocity,
            actual_distance,
            desired_distance,
            distance_error,
            velocity_error,
            acceleration
        ])

        self.csv_file.flush()

    def destroy_node(self):

        self.csv_file.close()
        super().destroy_node()


def main(args=None):

    rclpy.init(args=args)

    node = AdaptiveSlaveNode()

    rclpy.spin(node)

    node.destroy_node()

    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()

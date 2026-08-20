import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

import csv
import random


class SlaveNode(Node):

    def __init__(self):
        super().__init__('slave_node')

        self.master_velocity = 0.0
        self.master_position = 0.0

        self.slave_velocity = 18.0
        self.slave_position = -15.0

        self.kp = 0.5
        self.kv = 0.8

        self.d0 = 5.0
        self.h = 1.0

        self.dt = 0.1
        self.time = 0.0

        # Baseline experiment: no packet loss
        self.packet_loss_probability = 0.0

        # Do not start controller before receiving
        # the first master state
        self.master_state_received = False

        self.csv_file = open(
            'platooning_data_baseline.csv',
            'w',
            newline=''
        )

        self.csv_writer = csv.writer(self.csv_file)

        self.csv_writer.writerow([
            'time',
            'master_position',
            'slave_position',
            'master_velocity',
            'slave_velocity',
            'actual_distance',
            'desired_distance',
            'distance_error',
            'velocity_error'
        ])

        self.state_subscription = self.create_subscription(
            Float64MultiArray,
            '/master_state',
            self.state_callback,
            10
        )

        self.timer = self.create_timer(
            self.dt,
            self.control_loop
        )

    def state_callback(self, msg):

        # Simulated communication packet loss
        if random.random() < self.packet_loss_probability:
            self.get_logger().info('Master state packet lost!')
            return

        self.master_position = msg.data[0]
        self.master_velocity = msg.data[1]

        self.master_state_received = True

    def control_loop(self):

        # Wait until first valid communication packet
        if not self.master_state_received:
            return

        self.time += self.dt

        desired_distance = (
            self.d0 +
            self.h * self.slave_velocity
        )

        actual_distance = (
            self.master_position -
            self.slave_position
        )

        distance_error = (
            actual_distance -
            desired_distance
        )

        velocity_error = (
            self.master_velocity -
            self.slave_velocity
        )

        acceleration = (
            self.kp * distance_error +
            self.kv * velocity_error
        )

        self.slave_velocity += acceleration * self.dt
        self.slave_position += self.slave_velocity * self.dt

        self.csv_writer.writerow([
            self.time,
            self.master_position,
            self.slave_position,
            self.master_velocity,
            self.slave_velocity,
            actual_distance,
            desired_distance,
            distance_error,
            velocity_error
        ])

        self.csv_file.flush()

        self.get_logger().info(
            f'Actual Distance: {actual_distance:.2f} | '
            f'Desired Distance: {desired_distance:.2f} | '
            f'Distance Error: {distance_error:.2f} | '
            f'Velocity Error: {velocity_error:.2f}'
        )

    def destroy_node(self):

        self.csv_file.close()

        super().destroy_node()


def main(args=None):

    rclpy.init(args=args)

    node = SlaveNode()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

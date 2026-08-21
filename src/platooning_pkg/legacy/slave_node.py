import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

import csv
import random


class SlaveNode(Node):

    def __init__(self):
        super().__init__('slave_node')

        # ROS parameters
        self.declare_parameter('packet_loss_probability', 0.10)
        self.declare_parameter('random_seed', 1)
        self.declare_parameter('run_name', 'run')

        self.packet_loss_probability = float(
            self.get_parameter('packet_loss_probability').value
        )

        self.random_seed = int(
            self.get_parameter('random_seed').value
        )

        self.run_name = str(
            self.get_parameter('run_name').value
        )

        random.seed(self.random_seed)

        # Follower initial conditions
        self.slave_velocity = 18.0
        self.slave_position = -15.0

        # Last successfully received leader state
        self.master_position = 0.0
        self.master_velocity = 0.0
        self.master_state_time = 0.0

        # Controller parameters
        self.kp = 0.5
        self.kv = 0.8
        self.d0 = 5.0
        self.h = 1.0

        self.dt = 0.1
        self.control_time = 0.0

        # Packet counters
        self.total_packets = 0
        self.received_packets = 0
        self.lost_packets = 0

        # Wait for first successful packet
        self.first_packet_received = False

        filename = f'platooning_{self.run_name}.csv'

        self.csv_file = open(
            filename,
            'w',
            newline=''
        )

        self.csv_writer = csv.writer(self.csv_file)

        self.csv_writer.writerow([
            'control_time',
            'master_state_time',
            'information_age',
            'packet_received',
            'total_packets',
            'received_packets',
            'lost_packets',
            'actual_loss_rate',
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

        self.get_logger().info(
            f'Run: {self.run_name} | '
            f'Packet loss: {self.packet_loss_probability * 100:.0f}% | '
            f'Seed: {self.random_seed}'
        )

    def state_callback(self, msg):

        self.total_packets += 1

        # Simulated packet loss
        if random.random() < self.packet_loss_probability:
            self.lost_packets += 1
            return

        # Successful packet reception
        self.received_packets += 1

        self.master_state_time = float(msg.data[0])
        self.master_position = float(msg.data[1])
        self.master_velocity = float(msg.data[2])

        self.first_packet_received = True

    def control_loop(self):

        if not self.first_packet_received:
            return

        self.control_time += self.dt

        # Stop experiment automatically after 30 seconds
        if self.control_time > 30.0:
            self.get_logger().info('Slave experiment completed.')
            rclpy.shutdown()
            return

        information_age = max(
            0.0,
            self.control_time - self.master_state_time
        )

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

        self.slave_velocity += (
            acceleration * self.dt
        )

        self.slave_position += (
            self.slave_velocity * self.dt
        )

        if self.total_packets > 0:
            actual_loss_rate = (
                self.lost_packets /
                self.total_packets
            )
        else:
            actual_loss_rate = 0.0

        packet_received = (
            1 if information_age <= self.dt + 1e-6 else 0
        )

        self.csv_writer.writerow([
            self.control_time,
            self.master_state_time,
            information_age,
            packet_received,
            self.total_packets,
            self.received_packets,
            self.lost_packets,
            actual_loss_rate,
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

    def destroy_node(self):

        if self.total_packets > 0:
            final_loss_rate = (
                self.lost_packets /
                self.total_packets
            ) * 100.0

            self.get_logger().info(
                f'FINAL PACKET LOSS: '
                f'{self.lost_packets}/{self.total_packets} '
                f'= {final_loss_rate:.2f}%'
            )

        self.csv_file.close()

        super().destroy_node()


def main(args=None):

    rclpy.init(args=args)

    node = SlaveNode()

    rclpy.spin(node)

    node.destroy_node()

    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()

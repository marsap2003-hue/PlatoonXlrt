import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
import csv
import random


class FollowerNode(Node):

    def __init__(self):
        super().__init__('follower_node')

        self.leader_velocity = 0.0
        self.leader_position = 0.0

        self.follower_velocity = 18.0
        self.follower_position = -15.0

        self.kp = 0.5
        self.kv = 0.8
        self.d0 = 5.0
        self.h = 1.0
        self.dt = 0.1
        self.time = 0.0

        self.packet_loss_probability = 0.2

        self.csv_file = open('platooning_data_packet_loss.csv', 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow([
            'time',
            'leader_position',
            'follower_position',
            'leader_velocity',
            'follower_velocity',
            'distance_error'
        ])

        self.velocity_subscription = self.create_subscription(
            Float32,
            '/leader_velocity',
            self.velocity_callback,
            10
        )

        self.position_subscription = self.create_subscription(
            Float32,
            '/leader_position',
            self.position_callback,
            10
        )

        self.timer = self.create_timer(
            self.dt,
            self.control_loop
        )

    def velocity_callback(self, msg):
        if random.random() < self.packet_loss_probability:
            self.get_logger().info('Velocity packet lost!')
            return

        self.leader_velocity = msg.data

    def position_callback(self, msg):
        if random.random() < self.packet_loss_probability:
            self.get_logger().info('Position packet lost!')
            return

        self.leader_position = msg.data

    def control_loop(self):
        self.time = self.time + self.dt

        desired_distance = self.d0 + self.h * self.follower_velocity
        actual_distance = self.leader_position - self.follower_position
        error = actual_distance - desired_distance

        acceleration = (
            self.kp * error +
            self.kv * (self.leader_velocity - self.follower_velocity)
        )

        self.follower_velocity = self.follower_velocity + acceleration * self.dt
        self.follower_position = self.follower_position + self.follower_velocity * self.dt

        self.csv_writer.writerow([
            self.time,
            self.leader_position,
            self.follower_position,
            self.leader_velocity,
            self.follower_velocity,
            error
        ])
        self.csv_file.flush()

        self.get_logger().info(
            f'Leader Pos: {self.leader_position:.2f} | '
            f'Follower Pos: {self.follower_position:.2f} | '
            f'Distance Error: {error:.2f}'
        )

    def destroy_node(self):
        self.csv_file.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)

    node = FollowerNode()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

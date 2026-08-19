import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
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

        self.packet_loss_probability = 0.2

        self.csv_file = open('platooning_data_packet_loss.csv', 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow([
            'time',
            'master_position',
            'slave_position',
            'master_velocity',
            'slave_velocity',
            'distance_error'
        ])

        self.velocity_subscription = self.create_subscription(
            Float32,
            '/master_velocity',
            self.velocity_callback,
            10
        )

        self.position_subscription = self.create_subscription(
            Float32,
            '/master_position',
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

        self.master_velocity = msg.data

    def position_callback(self, msg):
        if random.random() < self.packet_loss_probability:
            self.get_logger().info('Position packet lost!')
            return

        self.master_position = msg.data

    def control_loop(self):
        self.time = self.time + self.dt

        desired_distance = self.d0 + self.h * self.slave_velocity
        actual_distance = self.master_position - self.slave_position
        error = actual_distance - desired_distance

        acceleration = (
            self.kp * error +
            self.kv * (self.master_velocity - self.slave_velocity)
        )

        self.slave_velocity = self.slave_velocity + acceleration * self.dt
        self.slave_position = self.slave_position + self.slave_velocity * self.dt

        self.csv_writer.writerow([
            self.time,
            self.master_position,
            self.slave_position,
            self.master_velocity,
            self.slave_velocity,
            error
        ])
        self.csv_file.flush()

        self.get_logger().info(
            f'Master Pos: {self.master_position:.2f} | '
            f'Slave Pos: {self.slave_position:.2f} | '
            f'Distance Error: {error:.2f}'
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

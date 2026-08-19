import csv
import time

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose


class DataLogger(Node):

    def __init__(self):
        super().__init__('data_logger')

        self.start_time = time.time()

        self.master_x = 0.0
        self.slave_x = 0.0

        self.master_received = False
        self.slave_received = False
        self.initialized = False

        self.previous_master_x = 0.0
        self.previous_slave_x = 0.0
        self.previous_time = 0.0

        self.master_velocity = 0.0
        self.slave_velocity = 0.0

        self.desired_distance = 5.0

        self.file = open('gazebo_platooning_data.csv', 'w', newline='')
        self.writer = csv.writer(self.file)

        self.writer.writerow([
            'time',
            'master_position',
            'slave_position',
            'master_velocity',
            'slave_velocity',
            'distance_error'
        ])

        self.create_subscription(
            Pose,
            '/master_gazebo_pose',
            self.master_callback,
            10
        )

        self.create_subscription(
            Pose,
            '/slave_gazebo_pose',
            self.slave_callback,
            10
        )

        self.timer = self.create_timer(0.1, self.log_data)

    def master_callback(self, msg):
        self.master_x = msg.position.x
        self.master_received = True

    def slave_callback(self, msg):
        self.slave_x = msg.position.x
        self.slave_received = True

    def log_data(self):
        current_time = time.time() - self.start_time

        if not self.master_received or not self.slave_received:
            return

        if not self.initialized:
            self.previous_master_x = self.master_x
            self.previous_slave_x = self.slave_x
            self.previous_time = current_time
            self.initialized = True
            return

        dt = current_time - self.previous_time

        if dt <= 0.0:
            return

        self.master_velocity = (
            self.master_x - self.previous_master_x
        ) / dt

        self.slave_velocity = (
            self.slave_x - self.previous_slave_x
        ) / dt

        actual_distance = self.master_x - self.slave_x
        distance_error = actual_distance - self.desired_distance

        self.writer.writerow([
            current_time,
            self.master_x,
            self.slave_x,
            self.master_velocity,
            self.slave_velocity,
            distance_error
        ])

        self.file.flush()

        self.get_logger().info(
            f't: {current_time:.2f} | '
            f'Master Pos: {self.master_x:.2f} | '
            f'Slave Pos: {self.slave_x:.2f} | '
            f'Master Vel: {self.master_velocity:.2f} | '
            f'Slave Vel: {self.slave_velocity:.2f} | '
            f'Error: {distance_error:.2f}'
        )

        self.previous_master_x = self.master_x
        self.previous_slave_x = self.slave_x
        self.previous_time = current_time

    def destroy_node(self):
        self.file.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)

    node = DataLogger()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

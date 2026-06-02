import csv
import time

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose


class DataLogger(Node):

    def __init__(self):
        super().__init__('data_logger')

        self.start_time = time.time()

        self.leader_x = 0.0
        self.follower_x = 0.0
        self.desired_distance = 5.0

        self.file = open('/home/ms/ros2_ws/gazebo_platooning_data.csv', 'w', newline='')
        self.writer = csv.writer(self.file)

        self.writer.writerow([
            'time',
            'leader_position',
            'follower_position',
            'distance_error'
        ])

        self.create_subscription(
            Pose,
            '/leader_gazebo_pose',
            self.leader_callback,
            10
        )

        self.create_subscription(
            Pose,
            '/follower_gazebo_pose',
            self.follower_callback,
            10
        )

        self.timer = self.create_timer(0.1, self.log_data)

    def leader_callback(self, msg):
        self.leader_x = msg.position.x

    def follower_callback(self, msg):
        self.follower_x = msg.position.x

    def log_data(self):
        current_time = time.time() - self.start_time

        actual_distance = self.leader_x - self.follower_x
        distance_error = actual_distance - self.desired_distance

        self.writer.writerow([
            current_time,
            self.leader_x,
            self.follower_x,
            distance_error
        ])

        self.file.flush()

        self.get_logger().info(
            f't: {current_time:.2f} | '
            f'Leader: {self.leader_x:.2f} | '
            f'Follower: {self.follower_x:.2f} | '
            f'Error: {distance_error:.2f}'
        )

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

import random
import time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose
import subprocess


class GazeboSlave(Node):

    def __init__(self):
        super().__init__('gazebo_slave')

        self.pose_publisher = self.create_publisher(
            Pose,
            '/slave_gazebo_pose',
            10
        )

        self.subscription = self.create_subscription(
            Pose,
            '/master_gazebo_pose',
            self.master_callback,
            10
        )

        self.master_x = 0.0
        self.master_y = 0.0

        self.slave_x = -8.0
        self.slave_y = 0.0
        self.z = 0.5

        self.d0 = 5.0
        self.kp = 0.5
        self.dt = 0.1

        # Communication impairment parameters
        # Baseline configuration: no delay and no packet loss
        self.communication_delay = 0.0
        self.packet_loss_probability = 0.0

        self.timer = self.create_timer(
            self.dt,
            self.update_position
        )

    def master_callback(self, msg):
        time.sleep(self.communication_delay)

        if random.random() < self.packet_loss_probability:
            return

        self.master_x = msg.position.x
        self.master_y = msg.position.y

    def update_position(self):

        desired_x = self.master_x - self.d0

        error = desired_x - self.slave_x

        velocity = self.kp * error

        self.slave_x = self.slave_x + velocity * self.dt

        pose_msg = Pose()
        pose_msg.position.x = self.slave_x
        pose_msg.position.y = self.slave_y
        pose_msg.position.z = self.z
        pose_msg.orientation.w = 1.0

        self.pose_publisher.publish(pose_msg)

        command = (
            'gz service -s /world/platoon_world/set_pose '
            '--reqtype gz.msgs.Pose '
            '--reptype gz.msgs.Boolean '
            '--timeout 1000 '
            f'--req \'name: "slave_vehicle" '
            f'position {{x: {self.slave_x} y: {self.slave_y} z: {self.z}}} '
            'orientation {w: 1}\''
        )

        subprocess.run(command, shell=True)

        self.get_logger().info(
            f'Master x: {self.master_x:.2f} | '
            f'Slave x: {self.slave_x:.2f} | '
            f'Error: {error:.2f}'
        )


def main(args=None):
    rclpy.init(args=args)

    node = GazeboSlave()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

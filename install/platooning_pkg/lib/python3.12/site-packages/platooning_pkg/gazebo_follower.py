import random
import time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose
import subprocess


class GazeboFollower(Node):

    def __init__(self):
        super().__init__('gazebo_follower')
        self.pose_publisher = self.create_publisher(
    Pose,
    '/follower_gazebo_pose',
    10
)
        self.subscription = self.create_subscription(
            Pose,
            '/leader_gazebo_pose',
            self.leader_callback,
            10
        )

        self.leader_x = 0.0
        self.leader_y = 0.0

        self.follower_x = -8.0
        self.follower_y = 0.0
        self.z = 0.5

        self.d0 = 5.0
        self.kp = 0.5
        self.dt = 0.1

        self.timer = self.create_timer(
            self.dt,
            self.update_position
        )

    def leader_callback(self, msg):
        time.sleep(0.0)

        if random.random() < 0.4:
            return
        self.leader_x = msg.position.x
        self.leader_y = msg.position.y

    def update_position(self):

        desired_x = self.leader_x - self.d0

        error = desired_x - self.follower_x

        velocity = self.kp * error

        self.follower_x = self.follower_x + velocity * self.dt
        pose_msg = Pose()
        pose_msg.position.x = self.follower_x
        pose_msg.position.y = self.follower_y
        pose_msg.position.z = self.z
        pose_msg.orientation.w = 1.0

        self.pose_publisher.publish(pose_msg)
        command = (
            'gz service -s /world/platoon_world/set_pose '
            '--reqtype gz.msgs.Pose '
            '--reptype gz.msgs.Boolean '
            '--timeout 1000 '
            f'--req \'name: "follower_vehicle" '
            f'position {{x: {self.follower_x} y: {self.follower_y} z: {self.z}}} '
            'orientation {w: 1}\''
        )

        subprocess.run(command, shell=True)

        self.get_logger().info(
            f'Leader x: {self.leader_x:.2f} | '
            f'Follower x: {self.follower_x:.2f} | '
            f'Error: {error:.2f}'
        )


def main(args=None):
    rclpy.init(args=args)

    node = GazeboFollower()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

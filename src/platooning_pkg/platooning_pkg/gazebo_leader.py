import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose
import subprocess


class GazeboLeader(Node):

    def __init__(self):
        super().__init__('gazebo_leader')

        self.pose_publisher = self.create_publisher(
            Pose,
            '/leader_gazebo_pose',
            10
        )

        self.x = 0.0
        self.y = 0.0
        self.z = 0.5

        self.velocity = 0.2
        self.dt = 0.1

        self.timer = self.create_timer(
            self.dt,
            self.update_position
        )

    def update_position(self):
        self.x = self.x + self.velocity * self.dt

        pose_msg = Pose()
        pose_msg.position.x = self.x
        pose_msg.position.y = self.y
        pose_msg.position.z = self.z
        pose_msg.orientation.w = 1.0

        self.pose_publisher.publish(pose_msg)

        command = (
            'gz service -s /world/platoon_world/set_pose '
            '--reqtype gz.msgs.Pose '
            '--reptype gz.msgs.Boolean '
            '--timeout 1000 '
            f'--req \'name: "leader_vehicle" '
            f'position {{x: {self.x} y: {self.y} z: {self.z}}} '
            'orientation {w: 1}\''
        )

        subprocess.run(command, shell=True)

        self.get_logger().info(
            f'Leader moved -> x: {self.x:.2f}, y: {self.y:.2f}'
        )


def main(args=None):
    rclpy.init(args=args)

    node = GazeboLeader()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

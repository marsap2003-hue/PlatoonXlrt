import math
import subprocess
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray


class GazeboCircularMaster(Node):

    def __init__(self):
        super().__init__('gazebo_circular_master')

        self.state_publisher = self.create_publisher(
            Float64MultiArray,
            '/gazebo_master_state',
            10
        )

        self.radius = 20.0
        self.z = 0.5

        # Longitudinal state along circular path
        self.s = 0.0
        self.velocity = 2.0

        self.dt = 0.1
        self.start_time = time.time()

        self.timer = self.create_timer(
            self.dt,
            self.update_position
        )

        self.get_logger().info(
            'Circular Gazebo Master started.'
        )

    def update_position(self):

        current_time = time.time() - self.start_time

        # Controlled disturbance:
        # constant speed -> braking -> reduced speed
        if 10.0 <= current_time < 15.0:
            acceleration = -0.15
        else:
            acceleration = 0.0

        self.velocity += acceleration * self.dt

        # Avoid negative velocity
        self.velocity = max(self.velocity, 0.0)

        self.s += self.velocity * self.dt

        theta = self.s / self.radius

        x = self.radius * math.cos(theta)
        y = self.radius * math.sin(theta)

        # Tangential orientation
        yaw = theta + math.pi / 2.0

        state_msg = Float64MultiArray()

        state_msg.data = [
            current_time,
            self.s,
            self.velocity
        ]

        self.state_publisher.publish(state_msg)

        command = (
            'gz service '
            '-s /world/platoon_circle_world/set_pose '
            '--reqtype gz.msgs.Pose '
            '--reptype gz.msgs.Boolean '
            '--timeout 1000 '
            f'--req \'name: "master_vehicle" '
            f'position {{x: {x} y: {y} z: {self.z}}} '
            f'orientation {{'
            f'z: {math.sin(yaw / 2.0)} '
            f'w: {math.cos(yaw / 2.0)}'
            f'}}\''
        )

        subprocess.run(
            command,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        self.get_logger().info(
            f't={current_time:.1f} s | '
            f's={self.s:.2f} m | '
            f'v={self.velocity:.2f} m/s'
        )


def main(args=None):

    rclpy.init(args=args)

    node = GazeboCircularMaster()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()

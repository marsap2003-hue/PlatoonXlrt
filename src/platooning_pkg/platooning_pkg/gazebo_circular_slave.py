import math
import subprocess

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray


class GazeboCircularSlave(Node):

    def __init__(self):
        super().__init__('gazebo_circular_slave')

        # -------------------------------------------------
        # ROS 2 parameters
        # -------------------------------------------------
        self.declare_parameter('slave_id', 1)
        self.declare_parameter(
            'predecessor_topic',
            '/gazebo_master_state'
        )
        self.declare_parameter(
            'state_topic',
            '/gazebo_slave1_state'
        )
        self.declare_parameter(
            'model_name',
            'slave1_vehicle'
        )
        self.declare_parameter(
            'initial_s',
            -5.0
        )

        self.slave_id = int(
            self.get_parameter('slave_id').value
        )

        self.predecessor_topic = str(
            self.get_parameter('predecessor_topic').value
        )

        self.state_topic = str(
            self.get_parameter('state_topic').value
        )

        self.model_name = str(
            self.get_parameter('model_name').value
        )

        self.s = float(
            self.get_parameter('initial_s').value
        )

        # -------------------------------------------------
        # Circular path
        # -------------------------------------------------
        self.radius = 20.0
        self.z = 0.5

        # -------------------------------------------------
        # Longitudinal controller
        # -------------------------------------------------
        self.velocity = 2.0

        self.d0 = 5.0
        self.kp = 0.5
        self.kv = 0.8

        self.dt = 0.1

        # Latest predecessor state
        self.predecessor_s = self.s + self.d0
        self.predecessor_velocity = self.velocity
        self.predecessor_time = 0.0

        # -------------------------------------------------
        # ROS communication
        # -------------------------------------------------
        self.state_publisher = self.create_publisher(
            Float64MultiArray,
            self.state_topic,
            10
        )

        self.subscription = self.create_subscription(
            Float64MultiArray,
            self.predecessor_topic,
            self.predecessor_callback,
            10
        )

        self.timer = self.create_timer(
            self.dt,
            self.update_position
        )

        self.get_logger().info(
            f'Circular Slave {self.slave_id} started | '
            f'Following: {self.predecessor_topic} | '
            f'Model: {self.model_name}'
        )

    def predecessor_callback(self, msg):

        if len(msg.data) < 3:
            return

        self.predecessor_time = float(msg.data[0])
        self.predecessor_s = float(msg.data[1])
        self.predecessor_velocity = float(msg.data[2])

    def update_position(self):

        # -------------------------------------------------
        # Predecessor-following controller
        # -------------------------------------------------
        actual_distance = (
            self.predecessor_s - self.s
        )

        distance_error = (
            actual_distance - self.d0
        )

        velocity_error = (
            self.predecessor_velocity -
            self.velocity
        )

        acceleration = (
            self.kp * distance_error +
            self.kv * velocity_error
        )

        self.velocity += (
            acceleration * self.dt
        )

        self.velocity = max(
            self.velocity,
            0.0
        )

        self.s += (
            self.velocity * self.dt
        )

        # -------------------------------------------------
        # Convert longitudinal coordinate s
        # to circular Gazebo coordinates
        # -------------------------------------------------
        theta = self.s / self.radius

        x = self.radius * math.cos(theta)
        y = self.radius * math.sin(theta)

        yaw = theta + math.pi / 2.0

        # -------------------------------------------------
        # Publish state for the next Slave
        # -------------------------------------------------
        state_msg = Float64MultiArray()

        state_msg.data = [
            self.predecessor_time,
            self.s,
            self.velocity
        ]

        self.state_publisher.publish(
            state_msg
        )

        # -------------------------------------------------
        # Move Gazebo model
        # -------------------------------------------------
        command = (
            'gz service '
            '-s /world/platoon_circle_world/set_pose '
            '--reqtype gz.msgs.Pose '
            '--reptype gz.msgs.Boolean '
            '--timeout 1000 '
            f'--req \'name: "{self.model_name}" '
            f'position {{'
            f'x: {x} '
            f'y: {y} '
            f'z: {self.z}'
            f'}} '
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
            f'Slave {self.slave_id} | '
            f's={self.s:.2f} m | '
            f'v={self.velocity:.2f} m/s | '
            f'd={actual_distance:.2f} m | '
            f'e={distance_error:.2f} m'
        )


def main(args=None):

    rclpy.init(args=args)

    node = GazeboCircularSlave()

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

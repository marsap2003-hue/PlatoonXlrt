import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32


class LeaderNode(Node):

    def __init__(self):
        super().__init__('leader_node')

        self.velocity_publisher = self.create_publisher(
            Float32,
            '/leader_velocity',
            10
        )

        self.position_publisher = self.create_publisher(
            Float32,
            '/leader_position',
            10
        )

        self.velocity = 20.0
        self.position = 0.0
        self.dt = 0.1
        self.time = 0.0

        self.timer = self.create_timer(
            self.dt,
            self.publish_data
        )

    def publish_data(self):
        self.time = self.time + self.dt

        if 10.0 <= self.time < 15.0:
            acceleration = -1.5
        else:
            acceleration = 0.0

        self.velocity = self.velocity + acceleration * self.dt

        if self.velocity < 0.0:
            self.velocity = 0.0

        self.position = self.position + self.velocity * self.dt

        velocity_msg = Float32()
        velocity_msg.data = self.velocity
        self.velocity_publisher.publish(velocity_msg)

        position_msg = Float32()
        position_msg.data = self.position
        self.position_publisher.publish(position_msg)

        self.get_logger().info(
            f'Leader time: {self.time:.2f} | '
            f'Leader position: {self.position:.2f} | '
            f'Leader velocity: {self.velocity:.2f}'
        )


def main(args=None):
    rclpy.init(args=args)

    node = LeaderNode()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

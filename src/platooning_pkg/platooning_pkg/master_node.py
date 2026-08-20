import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray


class MasterNode(Node):

    def __init__(self):
        super().__init__('master_node')

        self.state_publisher = self.create_publisher(
            Float64MultiArray,
            '/master_state',
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

        self.time += self.dt

        # Leader disturbance
        if 10.0 <= self.time < 15.0:
            acceleration = -1.5
        else:
            acceleration = 0.0

        self.velocity += acceleration * self.dt

        if self.velocity < 0.0:
            self.velocity = 0.0

        self.position += self.velocity * self.dt

        # Position and velocity are transmitted
        # together as one communication packet
        state_msg = Float64MultiArray()

        state_msg.data = [
            self.position,
            self.velocity
        ]

        self.state_publisher.publish(state_msg)

        self.get_logger().info(
            f'Master time: {self.time:.2f} | '
            f'Position: {self.position:.2f} | '
            f'Velocity: {self.velocity:.2f}'
        )


def main(args=None):

    rclpy.init(args=args)

    node = MasterNode()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

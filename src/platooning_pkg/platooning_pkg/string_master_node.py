import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray


class StringMasterNode(Node):

    def __init__(self):
        super().__init__('string_master_node')

        self.state_publisher = self.create_publisher(
            Float64MultiArray,
            '/master_state',
            10
        )

        # Initial conditions
        self.velocity = 20.0
        self.position = 0.0

        self.dt = 0.1
        self.time = 0.0

        self.timer = self.create_timer(
            self.dt,
            self.publish_state
        )

        self.get_logger().info(
            'String-stability Master started.'
        )

    def publish_state(self):

        self.time += self.dt

        # Same disturbance used in the previous experiments:
        # leader decelerates between 10 and 15 seconds.
        if 10.0 <= self.time < 15.0:
            acceleration = -1.5
        else:
            acceleration = 0.0

        self.velocity += acceleration * self.dt

        if self.velocity < 0.0:
            self.velocity = 0.0

        self.position += self.velocity * self.dt

        state_msg = Float64MultiArray()

        state_msg.data = [
            self.time,
            self.position,
            self.velocity
        ]

        self.state_publisher.publish(state_msg)

        if self.time > 30.0:
            self.get_logger().info(
                'String-stability experiment completed.'
            )
            rclpy.shutdown()
            return


def main(args=None):

    rclpy.init(args=args)

    node = StringMasterNode()

    rclpy.spin(node)

    node.destroy_node()

    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()

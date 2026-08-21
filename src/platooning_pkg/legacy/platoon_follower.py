import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

import csv


class PlatoonFollower(Node):

    def __init__(self):
        super().__init__('platoon_follower')

        # Parameters
        self.declare_parameter('vehicle_id', 1)
        self.declare_parameter('predecessor_topic', '/master_state')
        self.declare_parameter('initial_position', -25.0)
        self.declare_parameter('csv_name', 'vehicle1.csv')

        self.vehicle_id = int(
            self.get_parameter('vehicle_id').value
        )

        self.predecessor_topic = str(
            self.get_parameter('predecessor_topic').value
        )

        self.position = float(
            self.get_parameter('initial_position').value
        )

        self.csv_name = str(
            self.get_parameter('csv_name').value
        )

        # Initial velocity
        self.velocity = 20.0

        # Last predecessor state
        self.predecessor_time = 0.0
        self.predecessor_position = 0.0
        self.predecessor_velocity = 0.0

        self.state_received = False

        # Same controller parameters
        self.kp = 0.5
        self.kv = 0.8
        self.d0 = 5.0
        self.h = 1.0

        self.dt = 0.1
        self.time = 0.0

        # Publish this vehicle's state
        self.state_topic = f'/vehicle{self.vehicle_id}_state'

        self.state_publisher = self.create_publisher(
            Float64MultiArray,
            self.state_topic,
            10
        )

        # Subscribe to predecessor
        self.state_subscription = self.create_subscription(
            Float64MultiArray,
            self.predecessor_topic,
            self.predecessor_callback,
            10
        )

        # CSV
        self.csv_file = open(
            self.csv_name,
            'w',
            newline=''
        )

        self.csv_writer = csv.writer(self.csv_file)

        self.csv_writer.writerow([
            'time',
            'vehicle_id',
            'predecessor_position',
            'vehicle_position',
            'predecessor_velocity',
            'vehicle_velocity',
            'actual_distance',
            'desired_distance',
            'distance_error',
            'velocity_error'
        ])

        self.timer = self.create_timer(
            self.dt,
            self.control_loop
        )

        self.get_logger().info(
            f'Vehicle {self.vehicle_id} started | '
            f'Following: {self.predecessor_topic} | '
            f'Publishing: {self.state_topic}'
        )

    def predecessor_callback(self, msg):

        self.predecessor_time = float(msg.data[0])
        self.predecessor_position = float(msg.data[1])
        self.predecessor_velocity = float(msg.data[2])

        self.state_received = True

    def control_loop(self):

        if not self.state_received:
            return

        self.time += self.dt

        if self.time > 30.0:
            self.get_logger().info(
                f'Vehicle {self.vehicle_id} experiment completed.'
            )
            rclpy.shutdown()
            return

        # Constant time-headway spacing policy
        desired_distance = (
            self.d0 +
            self.h * self.velocity
        )

        actual_distance = (
            self.predecessor_position -
            self.position
        )

        distance_error = (
            actual_distance -
            desired_distance
        )

        velocity_error = (
            self.predecessor_velocity -
            self.velocity
        )

        acceleration = (
            self.kp * distance_error +
            self.kv * velocity_error
        )

        self.velocity += acceleration * self.dt
        self.position += self.velocity * self.dt

        # Publish own state for the next vehicle
        state_msg = Float64MultiArray()

        state_msg.data = [
            self.time,
            self.position,
            self.velocity
        ]

        self.state_publisher.publish(state_msg)

        self.csv_writer.writerow([
            self.time,
            self.vehicle_id,
            self.predecessor_position,
            self.position,
            self.predecessor_velocity,
            self.velocity,
            actual_distance,
            desired_distance,
            distance_error,
            velocity_error
        ])

        self.csv_file.flush()

    def destroy_node(self):

        self.csv_file.close()
        super().destroy_node()


def main(args=None):

    rclpy.init(args=args)

    node = PlatoonFollower()

    rclpy.spin(node)

    node.destroy_node()

    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

import csv
from collections import deque


class MultiSlaveNode(Node):

    def __init__(self):
        super().__init__('multi_slave_node')

        # Parameters
        self.declare_parameter('slave_id', 1)
        self.declare_parameter('predecessor_topic', '/master_state')
        self.declare_parameter('initial_position', -25.0)
        self.declare_parameter('csv_name', 'slave1_string.csv')
        self.declare_parameter('communication_delay', 0.0)

        self.slave_id = int(
            self.get_parameter('slave_id').value
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

        self.communication_delay = float(
            self.get_parameter('communication_delay').value
        )

        # Initial velocity
        self.velocity = 20.0

        # Controller parameters
        self.kp = 0.5
        self.kv = 0.8
        self.d0 = 5.0
        self.h = 1.0

        self.dt = 0.1
        self.experiment_duration = 30.0

        # Prevent repeated shutdown calls
        self.experiment_finished = False

        # Buffer for deterministic communication delay
        self.state_buffer = deque()

        # State topic published to next Slave
        self.state_topic = f'/slave{self.slave_id}_state'

        self.state_publisher = self.create_publisher(
            Float64MultiArray,
            self.state_topic,
            10
        )

        self.state_subscription = self.create_subscription(
            Float64MultiArray,
            self.predecessor_topic,
            self.predecessor_callback,
            10
        )

        # CSV output
        self.csv_file = open(
            self.csv_name,
            'w',
            newline=''
        )

        self.csv_writer = csv.writer(self.csv_file)

        self.csv_writer.writerow([
            'control_time',
            'predecessor_state_time',
            'information_age',
            'slave_id',
            'predecessor_position',
            'slave_position',
            'predecessor_velocity',
            'slave_velocity',
            'actual_distance',
            'desired_distance',
            'distance_error',
            'velocity_error',
            'acceleration'
        ])

        self.get_logger().info(
            f'Slave {self.slave_id} started | '
            f'Following: {self.predecessor_topic} | '
            f'Delay: {self.communication_delay:.1f} s'
        )

    def predecessor_callback(self, msg):

        if self.experiment_finished:
            return

        current_time = float(msg.data[0])
        predecessor_position = float(msg.data[1])
        predecessor_velocity = float(msg.data[2])

        # Store incoming predecessor state
        self.state_buffer.append((
            current_time,
            predecessor_position,
            predecessor_velocity
        ))

        target_time = (
            current_time - self.communication_delay
        )

        if target_time < 0.0:
            return

        delayed_state = None

        # Select newest predecessor state whose timestamp
        # is at least communication_delay old
        while (
            len(self.state_buffer) > 0 and
            self.state_buffer[0][0] <= target_time + 1e-6
        ):
            delayed_state = self.state_buffer.popleft()

        if delayed_state is None:
            return

        predecessor_state_time = delayed_state[0]
        delayed_position = delayed_state[1]
        delayed_velocity = delayed_state[2]

        self.control_step(
            current_time,
            predecessor_state_time,
            delayed_position,
            delayed_velocity
        )

    def control_step(
        self,
        control_time,
        predecessor_state_time,
        predecessor_position,
        predecessor_velocity
    ):

        information_age = (
            control_time - predecessor_state_time
        )

        # Constant-time-headway spacing policy
        desired_distance = (
            self.d0 +
            self.h * self.velocity
        )

        actual_distance = (
            predecessor_position -
            self.position
        )

        distance_error = (
            actual_distance -
            desired_distance
        )

        velocity_error = (
            predecessor_velocity -
            self.velocity
        )

        # Longitudinal control law
        acceleration = (
            self.kp * distance_error +
            self.kv * velocity_error
        )

        # Vehicle-state update
        self.velocity += (
            acceleration * self.dt
        )

        self.position += (
            self.velocity * self.dt
        )

        # Publish current Slave state.
        # This becomes predecessor information
        # for the next vehicle in the platoon.
        state_msg = Float64MultiArray()

        state_msg.data = [
            control_time,
            self.position,
            self.velocity
        ]

        self.state_publisher.publish(state_msg)

        # Log experiment data
        self.csv_writer.writerow([
            control_time,
            predecessor_state_time,
            information_age,
            self.slave_id,
            predecessor_position,
            self.position,
            predecessor_velocity,
            self.velocity,
            actual_distance,
            desired_distance,
            distance_error,
            velocity_error,
            acceleration
        ])

        self.csv_file.flush()

        # Graceful automatic shutdown
        if control_time >= self.experiment_duration:
            self.experiment_finished = True

            self.get_logger().info(
                f'Slave {self.slave_id} experiment completed.'
            )

            rclpy.shutdown()

    def destroy_node(self):

        if not self.csv_file.closed:
            self.csv_file.close()

        super().destroy_node()


def main(args=None):

    rclpy.init(args=args)

    node = MultiSlaveNode()

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

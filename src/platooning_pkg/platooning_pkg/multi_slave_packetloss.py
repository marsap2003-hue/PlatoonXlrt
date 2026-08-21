import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

import csv
import random


class MultiSlavePacketLoss(Node):

    def __init__(self):
        super().__init__('multi_slave_packetloss')

        self.declare_parameter('slave_id', 1)
        self.declare_parameter('predecessor_topic', '/master_state')
        self.declare_parameter('initial_position', -25.0)
        self.declare_parameter('csv_name', 'slave_packetloss.csv')
        self.declare_parameter('packet_loss_probability', 0.0)
        self.declare_parameter('headway', 1.0)
        self.declare_parameter('random_seed', 1)

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

        self.packet_loss_probability = float(
            self.get_parameter('packet_loss_probability').value
        )

        self.h = float(
            self.get_parameter('headway').value
        )

        self.random_seed = int(
            self.get_parameter('random_seed').value
        )

        random.seed(
            self.random_seed + 100 * self.slave_id
        )

        # Vehicle state
        self.velocity = 20.0

        # Controller
        self.kp = 0.5
        self.kv = 0.8
        self.d0 = 5.0
        self.dt = 0.1

        # Last successfully received predecessor state
        self.predecessor_position = 0.0
        self.predecessor_velocity = 0.0
        self.predecessor_state_time = 0.0

        # Latest time seen on the communication channel
        self.current_channel_time = 0.0

        self.first_packet_received = False
        self.first_message_seen = False

        # Packet counters
        self.total_packets = 0
        self.received_packets = 0
        self.lost_packets = 0

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

        self.csv_file = open(
            self.csv_name,
            'w',
            newline=''
        )

        self.csv_writer = csv.writer(self.csv_file)

        self.csv_writer.writerow([
            'time',
            'slave_id',
            'packet_loss_probability',
            'actual_loss_rate',
            'information_age',
            'predecessor_state_time',
            'predecessor_position',
            'slave_position',
            'predecessor_velocity',
            'slave_velocity',
            'actual_distance',
            'desired_distance',
            'distance_error',
            'velocity_error',
            'acceleration',
            'total_packets',
            'received_packets',
            'lost_packets'
        ])

        self.get_logger().info(
            f'Slave {self.slave_id} | '
            f'Loss: {self.packet_loss_probability * 100:.0f}% | '
            f'h: {self.h:.2f}'
        )

    def predecessor_callback(self, msg):

        # Every predecessor message carries the common simulation time
        message_time = float(msg.data[0])

        self.current_channel_time = message_time
        self.first_message_seen = True

        self.total_packets += 1

        # Simulated packet loss
        if random.random() < self.packet_loss_probability:
            self.lost_packets += 1

            # Even when packet is lost, controller still executes
            # using the last successfully received predecessor state.
            if self.first_packet_received:
                self.control_step()

            return

        # Successful reception
        self.received_packets += 1

        self.predecessor_state_time = message_time
        self.predecessor_position = float(msg.data[1])
        self.predecessor_velocity = float(msg.data[2])

        self.first_packet_received = True

        self.control_step()

    def control_step(self):

        if not self.first_packet_received:
            return

        # Both values now use the SAME simulation-time basis
        current_time = self.current_channel_time

        information_age = max(
            0.0,
            current_time - self.predecessor_state_time
        )

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

        self.velocity += (
            acceleration * self.dt
        )

        self.position += (
            self.velocity * self.dt
        )

        # Publish current slave state using common simulation time
        state_msg = Float64MultiArray()

        state_msg.data = [
            current_time,
            self.position,
            self.velocity
        ]

        self.state_publisher.publish(state_msg)

        if self.total_packets > 0:
            actual_loss_rate = (
                self.lost_packets /
                self.total_packets
            )
        else:
            actual_loss_rate = 0.0

        self.csv_writer.writerow([
            current_time,
            self.slave_id,
            self.packet_loss_probability,
            actual_loss_rate,
            information_age,
            self.predecessor_state_time,
            self.predecessor_position,
            self.position,
            self.predecessor_velocity,
            self.velocity,
            actual_distance,
            desired_distance,
            distance_error,
            velocity_error,
            acceleration,
            self.total_packets,
            self.received_packets,
            self.lost_packets
        ])

        self.csv_file.flush()

    def destroy_node(self):

        if self.total_packets > 0:
            final_loss = (
                self.lost_packets /
                self.total_packets
            ) * 100.0

            self.get_logger().info(
                f'Slave {self.slave_id} final packet loss: '
                f'{self.lost_packets}/{self.total_packets} '
                f'= {final_loss:.2f}%'
            )

        self.csv_file.close()

        super().destroy_node()


def main(args=None):

    rclpy.init(args=args)

    node = MultiSlavePacketLoss()

    rclpy.spin(node)

    node.destroy_node()

    if rclpy.ok():
        rclpy.shutdown()


if __name__ == '__main__':
    main()

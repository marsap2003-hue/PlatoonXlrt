import csv
import math
import os
import subprocess

import rclpy
from rclpy.node import Node


class GazeboCircularPlatoonImproved(Node):

    def __init__(self):
        super().__init__('gazebo_circular_platoon_improved')

        # Circular trajectory
        self.radius = 20.0
        self.z = 0.5

        # Simulation timing
        self.dt = 0.1
        self.sim_time = 0.0
        self.duration = 60.0

        # Controller parameters
        self.d0 = 5.0
        self.h = 1.25
        self.kp = 0.5
        self.kv = 0.8

        # Initial velocity
        initial_velocity = 2.0

        # Initial desired distance with CTH
        initial_desired_distance = (
            self.d0 +
            self.h * initial_velocity
        )

        # Initial longitudinal positions
        self.master_s = 0.0
        self.slave1_s = -initial_desired_distance
        self.slave2_s = -2.0 * initial_desired_distance
        self.slave3_s = -3.0 * initial_desired_distance

        # Initial velocities
        self.master_v = initial_velocity
        self.slave1_v = initial_velocity
        self.slave2_v = initial_velocity
        self.slave3_v = initial_velocity

        # Output directory
        results_dir = os.path.expanduser(
            '~/ros2_ws/src/platooning_pkg/'
            'results/gazebo_circular_improved'
        )

        os.makedirs(results_dir, exist_ok=True)

        self.csv_path = os.path.join(
            results_dir,
            'gazebo_circular_improved.csv'
        )

        self.csv_file = open(
            self.csv_path,
            'w',
            newline=''
        )

        self.writer = csv.writer(self.csv_file)

        self.writer.writerow([
            'time',
            'master_s',
            'slave1_s',
            'slave2_s',
            'slave3_s',
            'master_velocity',
            'slave1_velocity',
            'slave2_velocity',
            'slave3_velocity',
            'desired_distance_slave1',
            'desired_distance_slave2',
            'desired_distance_slave3',
            'distance_master_slave1',
            'distance_slave1_slave2',
            'distance_slave2_slave3',
            'error_slave1',
            'error_slave2',
            'error_slave3'
        ])

        self.finished = False

        self.timer = self.create_timer(
            self.dt,
            self.control_step
        )

        self.get_logger().info(
            'Improved circular Gazebo platoon started.'
        )

    def circular_pose(self, s):
        theta = s / self.radius

        x = self.radius * math.cos(theta)
        y = self.radius * math.sin(theta)

        yaw = theta + math.pi / 2.0

        return x, y, yaw

    def set_model_pose(self, model_name, s):
        x, y, yaw = self.circular_pose(s)

        command = (
            'gz service '
            '-s /world/platoon_circle_world/set_pose '
            '--reqtype gz.msgs.Pose '
            '--reptype gz.msgs.Boolean '
            '--timeout 1000 '
            f'--req \'name: "{model_name}" '
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

        return subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    def control_step(self):

        if self.finished:
            return

        # -------------------------------------------------
        # Store all states at timestep k
        # -------------------------------------------------
        master_s_k = self.master_s
        master_v_k = self.master_v

        slave1_s_k = self.slave1_s
        slave1_v_k = self.slave1_v

        slave2_s_k = self.slave2_s
        slave2_v_k = self.slave2_v

        slave3_s_k = self.slave3_s
        slave3_v_k = self.slave3_v

        # -------------------------------------------------
        # Master disturbance
        # -------------------------------------------------
        if 10.0 <= self.sim_time < 15.0:
            master_acceleration = -0.15
        else:
            master_acceleration = 0.0

        # -------------------------------------------------
        # Desired distances using Constant Time Headway
        # -------------------------------------------------
        desired1_k = (
            self.d0 +
            self.h * slave1_v_k
        )

        desired2_k = (
            self.d0 +
            self.h * slave2_v_k
        )

        desired3_k = (
            self.d0 +
            self.h * slave3_v_k
        )

        # -------------------------------------------------
        # Slave 1 controller
        # -------------------------------------------------
        distance1_k = (
            master_s_k -
            slave1_s_k
        )

        error1_k = (
            distance1_k -
            desired1_k
        )

        velocity_error1 = (
            master_v_k -
            slave1_v_k
        )

        acceleration1 = (
            self.kp * error1_k +
            self.kv * velocity_error1
        )

        # -------------------------------------------------
        # Slave 2 controller
        # -------------------------------------------------
        distance2_k = (
            slave1_s_k -
            slave2_s_k
        )

        error2_k = (
            distance2_k -
            desired2_k
        )

        velocity_error2 = (
            slave1_v_k -
            slave2_v_k
        )

        acceleration2 = (
            self.kp * error2_k +
            self.kv * velocity_error2
        )

        # -------------------------------------------------
        # Slave 3 controller
        # -------------------------------------------------
        distance3_k = (
            slave2_s_k -
            slave3_s_k
        )

        error3_k = (
            distance3_k -
            desired3_k
        )

        velocity_error3 = (
            slave2_v_k -
            slave3_v_k
        )

        acceleration3 = (
            self.kp * error3_k +
            self.kv * velocity_error3
        )

        # -------------------------------------------------
        # Update all velocities to timestep k+1
        # -------------------------------------------------
        self.master_v = max(
            master_v_k +
            master_acceleration * self.dt,
            0.0
        )

        self.slave1_v = max(
            slave1_v_k +
            acceleration1 * self.dt,
            0.0
        )

        self.slave2_v = max(
            slave2_v_k +
            acceleration2 * self.dt,
            0.0
        )

        self.slave3_v = max(
            slave3_v_k +
            acceleration3 * self.dt,
            0.0
        )

        # -------------------------------------------------
        # Update all positions to timestep k+1
        # -------------------------------------------------
        self.master_s = (
            master_s_k +
            self.master_v * self.dt
        )

        self.slave1_s = (
            slave1_s_k +
            self.slave1_v * self.dt
        )

        self.slave2_s = (
            slave2_s_k +
            self.slave2_v * self.dt
        )

        self.slave3_s = (
            slave3_s_k +
            self.slave3_v * self.dt
        )

        # -------------------------------------------------
        # Recalculate desired distances from updated states
        # -------------------------------------------------
        desired1 = (
            self.d0 +
            self.h * self.slave1_v
        )

        desired2 = (
            self.d0 +
            self.h * self.slave2_v
        )

        desired3 = (
            self.d0 +
            self.h * self.slave3_v
        )

        # -------------------------------------------------
        # Calculate final distances and errors
        # -------------------------------------------------
        distance1 = (
            self.master_s -
            self.slave1_s
        )

        distance2 = (
            self.slave1_s -
            self.slave2_s
        )

        distance3 = (
            self.slave2_s -
            self.slave3_s
        )

        error1 = (
            distance1 -
            desired1
        )

        error2 = (
            distance2 -
            desired2
        )

        error3 = (
            distance3 -
            desired3
        )

        # -------------------------------------------------
        # Update Gazebo models
        # -------------------------------------------------
        processes = [
            self.set_model_pose(
                'master_vehicle',
                self.master_s
            ),
            self.set_model_pose(
                'slave1_vehicle',
                self.slave1_s
            ),
            self.set_model_pose(
                'slave2_vehicle',
                self.slave2_s
            ),
            self.set_model_pose(
                'slave3_vehicle',
                self.slave3_s
            )
        ]

        for process in processes:
            process.wait()

        # -------------------------------------------------
        # Save synchronized results
        # -------------------------------------------------
        self.writer.writerow([
            self.sim_time,
            self.master_s,
            self.slave1_s,
            self.slave2_s,
            self.slave3_s,
            self.master_v,
            self.slave1_v,
            self.slave2_v,
            self.slave3_v,
            desired1,
            desired2,
            desired3,
            distance1,
            distance2,
            distance3,
            error1,
            error2,
            error3
        ])

        self.csv_file.flush()

        if abs(self.sim_time - round(self.sim_time)) < 1e-6:
            self.get_logger().info(
                f't={self.sim_time:.1f} s | '
                f'e1={error1:.3f} m | '
                f'e2={error2:.3f} m | '
                f'e3={error3:.3f} m'
            )

        self.sim_time += self.dt

        if self.sim_time >= self.duration:
            self.finished = True

            self.get_logger().info(
                'Improved circular Gazebo experiment completed.'
            )

            self.get_logger().info(
                f'CSV saved to: {self.csv_path}'
            )

            rclpy.shutdown()

    def destroy_node(self):

        if not self.csv_file.closed:
            self.csv_file.close()

        super().destroy_node()


def main(args=None):

    rclpy.init(args=args)

    node = GazeboCircularPlatoonImproved()

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

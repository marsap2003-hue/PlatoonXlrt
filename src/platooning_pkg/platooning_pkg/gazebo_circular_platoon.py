import csv
import math
import os
import subprocess

import rclpy
from rclpy.node import Node


class GazeboCircularPlatoon(Node):

    def __init__(self):
        super().__init__('gazebo_circular_platoon')

        # Circular trajectory
        self.radius = 20.0
        self.z = 0.5

        # Simulation timing
        self.dt = 0.1
        self.sim_time = 0.0
        self.duration = 60.0

        # Controller parameters
        self.d0 = 5.0
        self.kp = 0.5
        self.kv = 0.8

        # Initial longitudinal positions along the circular path
        self.master_s = 0.0
        self.slave1_s = -5.0
        self.slave2_s = -10.0
        self.slave3_s = -15.0

        # Initial velocities
        self.master_v = 2.0
        self.slave1_v = 2.0
        self.slave2_v = 2.0
        self.slave3_v = 2.0

        # Output directory
        results_dir = os.path.expanduser(
            '~/ros2_ws/src/platooning_pkg/'
            'results/gazebo_circular_sync'
        )

        os.makedirs(results_dir, exist_ok=True)

        self.csv_path = os.path.join(
            results_dir,
            'gazebo_circular_sync_data.csv'
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
            'Synchronized circular Gazebo platoon started.'
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
        # Slave 1 controller
        # -------------------------------------------------
        distance1_k = (
            master_s_k -
            slave1_s_k
        )

        error1_k = (
            distance1_k -
            self.d0
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
            self.d0
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
            self.d0
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
        # Calculate final distances for logging
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
            self.d0
        )

        error2 = (
            distance2 -
            self.d0
        )

        error3 = (
            distance3 -
            self.d0
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
            distance1,
            distance2,
            distance3,
            error1,
            error2,
            error3
        ])

        self.csv_file.flush()

        # Print approximately once per simulation second
        if abs(self.sim_time - round(self.sim_time)) < 1e-6:
            self.get_logger().info(
                f't={self.sim_time:.1f} s | '
                f'e1={error1:.3f} m | '
                f'e2={error2:.3f} m | '
                f'e3={error3:.3f} m'
            )

        self.sim_time += self.dt

        # -------------------------------------------------
        # Automatic finish
        # -------------------------------------------------
        if self.sim_time >= self.duration:
            self.finished = True

            self.get_logger().info(
                'Circular Gazebo experiment completed.'
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

    node = GazeboCircularPlatoon()

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

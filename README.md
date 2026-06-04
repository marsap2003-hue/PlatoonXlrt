# PlatoonXlrt

ROS2/Gazebo simulation of a simple vehicle platooning system with communication delay and packet loss evaluation.

## Overview

This project implements a vehicle platooning system using ROS2 and Gazebo. Two vehicles are simulated:

- Leader vehicle
- Follower vehicle

The leader moves with constant velocity and publishes its position through ROS2 topics. The follower receives the leader position and applies a proportional control law to maintain a desired inter-vehicle distance.

The effect of communication impairments is evaluated by introducing:

- Communication delays (200 ms, 500 ms, 1000 ms)
- Packet loss (10%, 20%, 40%)

Simulation data are logged and exported to CSV files for post-processing and visualization.

---

## Software Environment

- Ubuntu 24.04
- ROS2 Jazzy
- Gazebo Sim
- Python 3

---

## Workspace Structure

```text
ros2_ws/
├── src/
│   ├── platooning_pkg/
│   └── platoon_gazebo/
├── gazebo_platooning_data.csv
├── plot_gazebo_results.py
└── plot_results.py
```

## Main Files

### platooning_pkg

#### gazebo_leader.py

Leader vehicle node.

Responsibilities:

- Generates leader motion
- Publishes leader position
- Updates leader pose in Gazebo

#### gazebo_follower.py

Follower vehicle node.

Responsibilities:

- Receives leader position
- Computes distance error
- Applies platooning control law
- Updates follower pose in Gazebo

#### data_logger.py

Data acquisition node.

Records:

- Time
- Leader position
- Follower position
- Distance error

Data are saved into CSV files.

---

### platoon_gazebo

#### platoon_world.sdf

Gazebo simulation world.

Contains:

- Ground plane
- Leader vehicle model
- Follower vehicle model

---

## ROS2 Topics

### Published Topics

Leader:

```text
/leader_gazebo_pose
```

Type:

```text
geometry_msgs/msg/Pose
```

Follower:

```text
/follower_gazebo_pose
```

Type:

```text
geometry_msgs/msg/Pose
```

---

## Platooning Control Law

Desired distance:

```text
d0 = 5.0 m
```

Proportional gain:

```text
Kp = 0.5
```

Control equation:

```text
desired_position = leader_position - d0

error = desired_position - follower_position

velocity = Kp * error
```

---

## Communication Delay Experiments

Artificial communication delays were introduced inside the follower node using:

```python
time.sleep(...)
```

Tested values:

- 200 ms
- 500 ms
- 1000 ms

---

## Packet Loss Experiments

Packet loss was simulated through random message dropping:

```python
if random.random() < p:
    return
```

Tested values:

- 10 %
- 20 %
- 40 %

---

## Running the Simulation

### Build

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
```

### Start Gazebo

```bash
gz sim -r ~/ros2_ws/src/platoon_gazebo/worlds/platoon_world.sdf
```

### Start ROS2 Nodes

```bash
ros2 launch platoon_gazebo platoon_sim.launch.py
```

---

## Output Data

Simulation results are stored in CSV files and later processed using Python scripts.

Generated plots include:

- Vehicle positions
- Distance error
- Delay impact
- Packet loss impact

---

## Author

Marios Saparillas

Department of Electrical and Computer Engineering

Cyprus University of Technology

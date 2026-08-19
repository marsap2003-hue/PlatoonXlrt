# PlatoonXlrt

ROS2 and Gazebo implementation of a vehicle platooning system for the evaluation of communication delays and packet losses.

## Overview

This repository contains the implementation developed for the study of vehicle platooning under non-ideal Vehicle-to-Vehicle (V2V) communication conditions.

The project was developed using ROS2 Jazzy, Python and Gazebo Sim. The implemented system consists of a Master vehicle and a Slave vehicle. The Master communicates its state through ROS2 topics, while the Slave uses the received information to determine its motion and maintain the desired inter-vehicle distance.

The implementation includes:

- ROS2-based vehicle platooning simulation
- Gazebo-based vehicle platooning simulation
- Master and Slave ROS2 nodes
- Platooning control algorithms
- Communication delay simulation
- Packet loss simulation
- Data logging to CSV files
- Python scripts for result visualization and analysis

The communication experiments investigate:

- Baseline: 0 ms delay, 0% packet loss
- Communication delay: 200 ms, 500 ms and 1000 ms
- Packet loss: 10%, 20% and 40%

---

## Software Environment

The project was developed and tested using:

- Ubuntu 24.04
- ROS2 Jazzy
- Gazebo Sim
- Python 3

Python libraries used for data processing and visualization include:

- pandas
- matplotlib

---

## Repository Structure

```text
PlatoonXlrt/
├── src/
│   ├── platooning_pkg/
│   │   ├── platooning_pkg/
│   │   │   ├── master_node.py
│   │   │   ├── slave_node.py
│   │   │   ├── gazebo_master.py
│   │   │   ├── gazebo_slave.py
│   │   │   └── data_logger.py
│   │   ├── package.xml
│   │   └── setup.py
│   │
│   └── platoon_gazebo/
│       ├── launch/
│       │   └── platoon_sim.launch.py
│       ├── worlds/
│       │   └── platoon_world.sdf
│       ├── package.xml
│       └── setup.py
│
├── plot_results.py
├── plot_gazebo_results.py
└── README.md
```

---

# 1. ROS2 Platooning Implementation

The first implementation consists of two ROS2 nodes:

- `master_node.py`
- `slave_node.py`

## Master Node

The Master Node publishes:

```text
/master_velocity
/master_position
```

The Master starts with an initial velocity of 20 m/s.

Between 10 s and 15 s, a deceleration of -1.5 m/s² is applied. This creates a change in the Master motion that the Slave must respond to.

The simulation is updated every 0.1 s.

## Slave Node

The Slave subscribes to the Master position and velocity.

Initial conditions:

```text
Slave velocity = 18 m/s
Slave position = -15 m
```

Controller parameters:

```text
Kp = 0.5
Kv = 0.8
d0 = 5.0 m
h = 1.0 s
dt = 0.1 s
```

The desired distance is calculated using a constant-time-headway spacing policy:

```text
desired_distance = d0 + h * slave_velocity
```

The distance error is:

```text
actual_distance = master_position - slave_position
error = actual_distance - desired_distance
```

The Slave acceleration is calculated as:

```text
acceleration =
    Kp * error +
    Kv * (master_velocity - slave_velocity)
```

The Slave Node also contains a packet-loss mechanism based on random message dropping.

Simulation results are recorded in CSV format and can be visualized using:

```bash
python3 plot_results.py
```

The generated plots include:

- Master and Slave positions
- Master and Slave velocities
- Distance error

---

# 2. Gazebo Platooning Implementation

A second implementation was developed using ROS2 and Gazebo Sim.

The Gazebo simulation contains two simplified vehicle models:

- `master_vehicle`
- `slave_vehicle`

The simulation world is defined in:

```text
src/platoon_gazebo/worlds/platoon_world.sdf
```

The Master initially starts at:

```text
x = 0 m
```

and the Slave at:

```text
x = -8 m
```

The desired inter-vehicle distance is:

```text
d0 = 5.0 m
```

## Gazebo Master

The Gazebo Master is implemented in:

```text
gazebo_master.py
```

The node publishes the Master pose through:

```text
/master_gazebo_pose
```

Message type:

```text
geometry_msgs/msg/Pose
```

The Master moves with constant velocity:

```text
0.2 m/s
```

with an update period of:

```text
0.1 s
```

Its pose in Gazebo is updated through the Gazebo `/set_pose` service.

## Gazebo Slave

The Gazebo Slave is implemented in:

```text
gazebo_slave.py
```

It subscribes to:

```text
/master_gazebo_pose
```

and publishes:

```text
/slave_gazebo_pose
```

The controller uses the desired Master-relative position:

```text
desired_x = master_x - d0
```

The position error is:

```text
error = desired_x - slave_x
```

and the Slave velocity command is calculated using:

```text
velocity = Kp * error
```

where:

```text
Kp = 0.5
d0 = 5.0 m
dt = 0.1 s
```

---

# 3. Communication Impairments

Communication limitations were introduced in the `gazebo_slave.py` node in order to evaluate the performance of the platooning system under non-ideal V2V communication.

The two parameters are:

```python
self.communication_delay = 0.0
self.packet_loss_probability = 0.0
```

The default configuration corresponds to the baseline scenario with no communication delay and no packet loss.

## 3.1 Baseline

Use:

```python
self.communication_delay = 0.0
self.packet_loss_probability = 0.0
```

This represents ideal communication conditions.

## 3.2 Communication Delay Experiments

For the delay experiments, packet loss remains disabled:

```python
self.packet_loss_probability = 0.0
```

### 200 ms

```python
self.communication_delay = 0.2
```

### 500 ms

```python
self.communication_delay = 0.5
```

### 1000 ms

```python
self.communication_delay = 1.0
```

The delay is applied when Master messages are received by the Slave.

## 3.3 Packet Loss Experiments

For the packet-loss experiments, communication delay is disabled:

```python
self.communication_delay = 0.0
```

### 10% Packet Loss

```python
self.packet_loss_probability = 0.1
```

### 20% Packet Loss

```python
self.packet_loss_probability = 0.2
```

### 40% Packet Loss

```python
self.packet_loss_probability = 0.4
```

Packet loss is implemented by randomly discarding received Master messages.

When a message is discarded, the Slave continues operating using the most recently received Master information.

---

# 4. Building the ROS2 Workspace

Clone the repository:

```bash
git clone https://github.com/marsap2003-hue/PlatoonXlrt.git
```

Enter the repository:

```bash
cd PlatoonXlrt
```

Build the ROS2 packages:

```bash
colcon build
```

Source the workspace:

```bash
source install/setup.bash
```

---

# 5. Running the Gazebo Simulation

## Step 1 - Start Gazebo

From the repository root, run:

```bash
gz sim -r src/platoon_gazebo/worlds/platoon_world.sdf
```

The Gazebo environment should open with the Master and Slave vehicles.

## Step 2 - Start the ROS2 Nodes

Open a second terminal.

Navigate to the repository and source the workspace:

```bash
cd PlatoonXlrt
source install/setup.bash
```

Run:

```bash
ros2 launch platoon_gazebo platoon_sim.launch.py
```

The launch file starts:

```text
gazebo_master
gazebo_slave
data_logger
```

The Master and Slave should now move in the Gazebo environment.

---

# 6. Data Logging

The `data_logger.py` node subscribes to:

```text
/master_gazebo_pose
/slave_gazebo_pose
```

Data are recorded every 0.1 s.

The following variables are stored:

```text
time
master_position
slave_position
distance_error
```

The distance error is calculated as:

```text
actual_distance = master_position - slave_position
distance_error = actual_distance - desired_distance
```

with:

```text
desired_distance = 5.0 m
```

The results are stored in:

```text
gazebo_platooning_data.csv
```

Note: the CSV file is opened in write mode. Therefore, a new simulation run replaces the previous contents of the file. Save or rename the CSV file after each experiment if the results need to be preserved.

---

# 7. Generating the Gazebo Plots

After completing a simulation, stop the ROS2 nodes using:

```text
Ctrl+C
```

Then run:

```bash
python3 plot_gazebo_results.py
```

The script reads:

```text
gazebo_platooning_data.csv
```

and generates:

```text
gazebo_positions.png
gazebo_distance_error.png
```

The first plot compares the Master and Slave positions.

The second plot presents the distance error over time.

---

# 8. Reproducing the Experimental Scenarios

The following procedure can be used to reproduce each experiment.

## Baseline

Set in `gazebo_slave.py`:

```python
self.communication_delay = 0.0
self.packet_loss_probability = 0.0
```

Build and source the workspace:

```bash
colcon build
source install/setup.bash
```

Start Gazebo and the ROS2 nodes and collect the results.

## Delay Experiments

Repeat the simulation using:

```text
200 ms  -> communication_delay = 0.2
500 ms  -> communication_delay = 0.5
1000 ms -> communication_delay = 1.0
```

with:

```python
self.packet_loss_probability = 0.0
```

After changing the source code, rebuild and source the workspace before running the next experiment:

```bash
colcon build
source install/setup.bash
```

## Packet Loss Experiments

Repeat the simulation using:

```text
10% -> packet_loss_probability = 0.1
20% -> packet_loss_probability = 0.2
40% -> packet_loss_probability = 0.4
```

with:

```python
self.communication_delay = 0.0
```

Again, rebuild and source the workspace after changing the parameters.

---

# 9. Experimental Outputs

The experiments allow comparison between:

- Baseline operation
- 200 ms communication delay
- 500 ms communication delay
- 1000 ms communication delay
- 10% packet loss
- 20% packet loss
- 40% packet loss

The main performance indicator is the inter-vehicle distance error.

The results show how increasing communication impairment affects the ability of the Slave to maintain the desired distance from the Master.

---

## Author

Marios Saparillas

Department of Electrical and Computer Engineering  
Cyprus University of Technology

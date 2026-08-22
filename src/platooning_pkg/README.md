# PlatoonXlrt

ROS 2 implementation and simulation framework for connected vehicle platooning with communication delay, packet loss, time-headway analysis, string-stability evaluation, and multi-vehicle Gazebo simulation.

The project was developed as part of a thesis on Vehicle Platooning and Cooperative Adaptive Cruise Control (CACC).

---

## Overview

The final platoon architecture consists of one leader vehicle and three follower vehicles:

```text
Master -> Slave 1 -> Slave 2 -> Slave 3
```

A predecessor-following information-flow topology is used. Each follower receives state information from its immediate predecessor and adjusts its motion according to the implemented spacing-control strategy.

The repository includes experiments for:

- Baseline platooning operation
- Communication delay
- Packet loss
- Time-headway variation
- Original vs improved controller configurations
- Multi-vehicle string-stability evaluation
- Circular multi-vehicle Gazebo simulation
- Data logging and generation of thesis figures

---

## Software Environment

The project was developed using:

- Ubuntu 24.04
- ROS 2 Jazzy Jalisco
- Python 3
- Gazebo Sim
- NumPy
- pandas
- matplotlib

---

## Platoon Architecture

The main multi-vehicle architecture is:

```text
Master -> Slave 1 -> Slave 2 -> Slave 3
```

The Master defines the reference motion of the platoon.

Each Slave follows its immediate predecessor:

- Slave 1 follows the Master
- Slave 2 follows Slave 1
- Slave 3 follows Slave 2

ROS 2 topics are used as an abstract representation of V2V information exchange between the vehicles.

The implementation therefore focuses on the interaction between vehicle control and communication impairments rather than on the detailed modelling of a specific wireless communication protocol.

---

## Spacing Policy and Controller

For follower vehicle `i`, the actual inter-vehicle distance is defined as:

```text
d_i = x_(i-1) - x_i
```

where `x_(i-1)` is the position of the predecessor and `x_i` is the position of the follower.

For the Constant Time Headway (CTH) spacing policy, the desired distance is:

```text
d_des,i = d0 + h * v_i
```

where:

- `d0` is the standstill distance
- `h` is the time headway
- `v_i` is the follower velocity

The spacing error is:

```text
e_i = d_i - d_des,i
```

The follower acceleration command is based on the spacing error and the relative velocity:

```text
a_i = Kp * e_i + Kv * (v_(i-1) - v_i)
```

The controller parameters used in the final numerical configuration are:

```text
Kp = 0.5
Kv = 0.8
d0 = 5.0 m
```

---

## Repository Structure

The main ROS 2 package contains the vehicle nodes, launch files, experiment results, plotting scripts, and final thesis figures.

A simplified structure is:

```text
ros2_ws/src/
|
|-- platooning_pkg/
|   |
|   |-- platooning_pkg/
|   |   |-- string_master_node.py
|   |   |-- multi_slave_node.py
|   |   |-- adaptive_slave_node.py
|   |   |-- multi_slave_packetloss.py
|   |   |-- gazebo_master.py
|   |   |-- gazebo_slave.py
|   |   |-- gazebo_circular_master.py
|   |   |-- gazebo_circular_slave.py
|   |   |-- gazebo_circular_logger.py
|   |   |-- gazebo_circular_platoon.py
|   |   `-- gazebo_circular_platoon_improved.py
|   |
|   |-- launch/
|   |   |-- string_stability_baseline.launch.py
|   |   `-- gazebo_circular_platoon.launch.py
|   |
|   |-- scripts/
|   |   |-- plot_delay_comparison.py
|   |   |-- plot_headway_comparison.py
|   |   |-- plot_original_vs_improved.py
|   |   |-- plot_packet_loss_comparison.py
|   |   |-- plot_packet_loss_improvement.py
|   |   `-- plot_circular_gazebo_final.py
|   |
|   |-- results/
|   |-- thesis_final_plots/
|   |-- setup.py
|   |-- package.xml
|   `-- README.md
|
`-- platoon_gazebo/
    `-- worlds/
        `-- platoon_circle_world.sdf
```

---

## Build Instructions

Open a terminal and build the ROS 2 package:

```bash
cd ~/ros2_ws

source /opt/ros/jazzy/setup.bash

colcon build \
--packages-select platooning_pkg \
--symlink-install

source install/setup.bash
```

The package executables can be checked using:

```bash
ros2 pkg executables platooning_pkg
```

---

## Communication Delay Experiments

Communication delay is introduced to investigate the effect of outdated predecessor information on platoon behaviour.

The following deterministic communication delays are examined:

```text
0 ms
200 ms
500 ms
1000 ms
```

Instead of intentionally blocking the entire node execution, predecessor states can be stored and an older state selected according to the required communication delay.

This allows the follower controller to operate using information corresponding approximately to:

```text
t - tau
```

where `tau` represents the imposed communication delay.

The delay experiments are evaluated using quantities including:

- spacing error
- vehicle velocity
- actual distance
- desired distance
- disturbance propagation along the platoon

---

## Packet Loss Experiments

Packet loss is introduced probabilistically.

The following nominal packet-loss probabilities are examined:

```text
0%
10%
20%
40%
```

When an update is lost, the follower continues using the last successfully received predecessor information until a new update becomes available.

Because packet loss is stochastic, the actual packet-loss rate observed during an experiment can differ slightly from the nominal probability.

The experiments allow the effect of increasingly unreliable communication on the platoon response to be evaluated.

---

## Time-Headway Analysis

The influence of the Constant Time Headway parameter is evaluated using:

```text
h = 1.00 s
h = 1.25 s
h = 1.50 s
h = 1.75 s
h = 2.00 s
```

The headway sweep is performed under a severe communication-delay condition of:

```text
1000 ms
```

For the controller configuration and disturbance scenario examined in this project, the configuration:

```text
h = 1.25 s
```

produced the most favourable spacing-error behaviour among the tested values.

It was therefore selected as the improved time-headway configuration for subsequent comparisons.

This result applies to the examined simulation configuration and is not intended to represent a universally optimal time-headway value.

---

## String-Stability Evaluation

The four-vehicle architecture allows the propagation of disturbances to be examined along the platoon.

For each follower, the L2 norm of the spacing error can be calculated as:

```text
||e_i||_2
```

The propagation ratios between consecutive followers are defined as:

```text
G21 = ||e2||2 / ||e1||2

G32 = ||e3||2 / ||e2||2
```

A propagation ratio below 1 indicates attenuation of the examined spacing-error metric between the corresponding followers for the specific experiment.

A ratio greater than 1 indicates amplification of that metric.

These quantities are used as experimental indicators of disturbance propagation. They are not presented as a general mathematical proof of string stability.

---

# Circular Multi-Vehicle Gazebo Experiment

A circular Gazebo experiment was developed to provide a complementary visual and quantitative evaluation of the four-vehicle platoon.

The Gazebo platoon consists of:

```text
Master -> Slave 1 -> Slave 2 -> Slave 3
```

The vehicles move along a circular trajectory with radius:

```text
R = 20 m
```

A circular trajectory was selected so that the vehicles can be observed over a longer time interval without requiring an extremely long straight simulation environment.

The experiment duration is:

```text
60 s
```

with a simulation timestep of:

```text
0.1 s
```

resulting in:

```text
600 samples
```

for each complete experiment.

---

## Circular Gazebo World

The circular Gazebo world is stored in:

```text
src/platoon_gazebo/worlds/platoon_circle_world.sdf
```

From the ROS 2 workspace, start Gazebo using:

```bash
cd ~/ros2_ws

gz sim src/platoon_gazebo/worlds/platoon_circle_world.sdf
```

If the simulation opens in a paused state, press Play in the Gazebo interface.

---

## Leader Disturbance in the Circular Experiment

The Master initially travels at:

```text
2.0 m/s
```

A controlled deceleration is introduced during:

```text
10 s <= t < 15 s
```

with:

```text
a_M = -0.15 m/s^2
```

The Master therefore decreases its speed from:

```text
2.0 m/s
```

to:

```text
1.25 m/s
```

This speed change acts as the disturbance used to evaluate the response and propagation behaviour of the followers.

---

## Original Circular Gazebo Configuration

The original circular configuration uses a constant desired spacing of:

```text
5.0 m
```

With the Gazebo world already running, execute:

```bash
cd ~/ros2_ws

source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 run platooning_pkg gazebo_circular_platoon
```

The original experiment produced the following L2 spacing-error propagation ratios:

```text
G21 = 1.1826
G32 = 1.2157
```

Both ratios are greater than 1 for this experiment, indicating amplification of the examined spacing-error metric toward the downstream vehicles.

The stored original dataset is:

```text
results/gazebo_circular_sync/gazebo_circular_original.csv
```

---

## Improved Circular Gazebo Configuration

The improved circular experiment applies the Constant Time Headway spacing policy:

```text
d_des,i = d0 + h * v_i
```

with:

```text
d0 = 5.0 m
h = 1.25 s
```

With Gazebo already running, execute:

```bash
cd ~/ros2_ws

source /opt/ros/jazzy/setup.bash
source install/setup.bash

ros2 run platooning_pkg gazebo_circular_platoon_improved
```

At the initial Master velocity of:

```text
2.0 m/s
```

the desired distance is:

```text
d_des = 5.0 + 1.25 * 2.0
      = 7.5 m
```

After the vehicles converge to:

```text
1.25 m/s
```

the desired distance becomes:

```text
d_des = 5.0 + 1.25 * 1.25
      = 6.5625 m
```

The improved circular experiment produced:

```text
G21 = 0.8332
G32 = 0.8647
```

Both ratios are below 1 for the tested disturbance, indicating attenuation of the examined spacing-error metric along the platoon.

The measured peak absolute spacing errors were:

```text
Slave 1 = 0.0079 m
Slave 2 = 0.0060 m
Slave 3 = 0.0051 m
```

The corresponding L2 spacing-error values were:

```text
Slave 1 = 0.0165
Slave 2 = 0.0138
Slave 3 = 0.0119
```

The improved dataset is stored in:

```text
results/gazebo_circular_improved/gazebo_circular_improved.csv
```

---

## Gazebo Implementation Note

The circular Gazebo experiment uses kinematic pose updates through the Gazebo `set_pose` service.

The vehicle poses are updated using the service:

```text
/world/platoon_world/set_pose
```

The Gazebo experiment should therefore be interpreted as:

- multi-vehicle functional validation
- kinematic validation
- visualization of circular platooning behaviour
- quantitative evaluation of spacing-error propagation

It is not intended to represent a complete force-based vehicle-dynamics simulation.

The implementation does not model detailed:

- tire-road interaction
- wheel dynamics
- steering actuator dynamics
- braking actuator dynamics
- powertrain dynamics

The numerical ROS 2 experiments remain the main experimental platform for the detailed communication-delay and packet-loss analysis.

---

## Circular Gazebo Results

The original circular experiment produced:

```text
G21 = 1.1826
G32 = 1.2157
```

while the improved CTH configuration produced:

```text
G21 = 0.8332
G32 = 0.8647
```

Therefore, for the examined Gazebo disturbance, the original configuration exhibited amplification of the selected spacing-error metric, whereas the improved CTH configuration exhibited attenuation.

The improved experiment also converged to the expected final desired distance:

```text
6.5625 m
```

for all three follower relationships when the final velocity reached:

```text
1.25 m/s
```

---

## Generate Final Circular Gazebo Plots

The final Gazebo plots can be generated using:

```bash
cd ~/ros2_ws/src/platooning_pkg

python3 scripts/plot_circular_gazebo_final.py
```

The script generates:

```text
gazebo_circular_original_vs_improved.png
gazebo_circular_improved_velocities.png
gazebo_circular_improved_distances.png
```

The figures are stored in:

```text
thesis_final_plots/
```

---

## Final Thesis Figures

The `thesis_final_plots/` directory contains the principal plots used for the final analysis, including:

```text
delay_comparison_slave1.png
headway_comparison_slave1.png
original_vs_improved_delay1000.png
original_vs_improved_loss40.png
packet_loss_comparison_slave1.png
string_stability_spacing_error.png
string_stability_velocities.png
gazebo_circular_original_vs_improved.png
gazebo_circular_improved_velocities.png
gazebo_circular_improved_distances.png
```

These figures summarize the principal communication, controller, string-stability, and Gazebo experiments performed in the project.

---

## Plotting Scripts

The repository contains Python scripts for reproducing the principal comparison figures:

```text
scripts/plot_delay_comparison.py
scripts/plot_headway_comparison.py
scripts/plot_original_vs_improved.py
scripts/plot_packet_loss_comparison.py
scripts/plot_packet_loss_improvement.py
scripts/plot_circular_gazebo_final.py
```

The scripts use the stored CSV experiment data to generate the plots used in the final analysis.

---

## Experimental Results

The `results/` directory contains data and figures from the different experiment categories, including:

- baseline experiments
- communication-delay experiments
- packet-loss experiments
- time-headway experiments
- improved-controller comparisons
- circular Gazebo experiments

The stored CSV files allow the principal quantitative results to be recalculated and plotted without rerunning every experiment.

---

## Reproducibility

The repository contains the main components required to reproduce and inspect the thesis experiments:

- ROS 2 nodes
- launch files
- controller implementations
- communication-impairment implementations
- Gazebo world
- circular Gazebo nodes
- experiment CSV files
- plotting scripts
- final thesis plots

The source code and stored datasets therefore provide a reproducible record of the simulation methodology and the principal results presented in the thesis.

---

## Scope and Limitations

The project focuses on simulation-based evaluation of vehicle platooning under controlled communication impairments.

The results should be interpreted within the specific:

- controller configuration
- spacing policy
- communication model
- vehicle model
- disturbance profile
- simulation environment

used in the experiments.

The project does not claim a general mathematical proof of string stability.

The ROS 2 communication model is an abstraction of V2V communication and does not implement a complete wireless-network stack.

Similarly, the Gazebo experiment is primarily a kinematic validation and visualization environment rather than a high-fidelity vehicle-dynamics simulation.

Future extensions could include:

- more detailed vehicle dynamics
- realistic steering and wheel models
- explicit V2X network simulation
- variable communication delay
- burst packet loss
- larger platoons
- additional information-flow topologies
- hardware or real-vehicle validation

---

## License

MIT

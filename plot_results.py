import pandas as pd
import matplotlib.pyplot as plt

# =========================
# Load CSV data
# =========================

data = pd.read_csv('platooning_data_packet_loss.csv')

# =========================
# Extract variables
# =========================

time = data['time']

leader_position = data['leader_position']
follower_position = data['follower_position']

leader_velocity = data['leader_velocity']
follower_velocity = data['follower_velocity']

distance_error = data['distance_error']

# =========================
# Position plot
# =========================

plt.figure(figsize=(8,5))

plt.plot(time, leader_position, label='Leader Position')
plt.plot(time, follower_position, label='Follower Position')

plt.xlabel('Time (s)')
plt.ylabel('Position (m)')

plt.title('ROS2 Vehicle Positions')

plt.legend()
plt.grid(True)

plt.show()

# =========================
# Velocity plot
# =========================

plt.figure(figsize=(8,5))

plt.plot(time, leader_velocity, label='Leader Velocity')
plt.plot(time, follower_velocity, label='Follower Velocity')

plt.xlabel('Time (s)')
plt.ylabel('Velocity (m/s)')

plt.title('ROS2 Vehicle Velocities')

plt.legend()
plt.grid(True)

plt.show()

# =========================
# Distance error plot
# =========================

plt.figure(figsize=(8,5))

plt.plot(time, distance_error)

plt.xlabel('Time (s)')
plt.ylabel('Distance Error (m)')

plt.title('ROS2 Distance Error')

plt.grid(True)

plt.show()

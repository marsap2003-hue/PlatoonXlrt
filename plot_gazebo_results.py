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

master_position = data['master_position']
slave_position = data['slave_position']

master_velocity = data['master_velocity']
slave_velocity = data['slave_velocity']

distance_error = data['distance_error']

# =========================
# Position plot
# =========================

plt.figure(figsize=(8,5))

plt.plot(time, master_position, label='Master Position')
plt.plot(time, slave_position, label='Slave Position')

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

plt.plot(time, master_velocity, label='Master Velocity')
plt.plot(time, slave_velocity, label='Slave Velocity')

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

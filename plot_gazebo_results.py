import pandas as pd
import matplotlib.pyplot as plt

# =========================
# Load Gazebo CSV data
# =========================

data = pd.read_csv('gazebo_platooning_data.csv')

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

plt.figure(figsize=(8, 5))

plt.plot(time, master_position, label='Master Position')
plt.plot(time, slave_position, label='Slave Position')

plt.xlabel('Time (s)')
plt.ylabel('Position (m)')
plt.title('Gazebo Vehicle Positions')

plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig('gazebo_positions.png', dpi=300)
plt.show()

# =========================
# Velocity plot
# =========================

plt.figure(figsize=(8, 5))

plt.plot(time, master_velocity, label='Master Velocity')
plt.plot(time, slave_velocity, label='Slave Velocity')

plt.xlabel('Time (s)')
plt.ylabel('Velocity (m/s)')
plt.title('Gazebo Vehicle Velocities')

plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig('gazebo_velocities.png', dpi=300)
plt.show()

# =========================
# Distance error plot
# =========================

plt.figure(figsize=(8, 5))

plt.plot(time, distance_error, label='Distance Error')

plt.xlabel('Time (s)')
plt.ylabel('Distance Error (m)')
plt.title('Gazebo Distance Error')

plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig('gazebo_distance_error.png', dpi=300)
plt.show()

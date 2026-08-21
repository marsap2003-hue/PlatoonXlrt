import pandas as pd
import matplotlib.pyplot as plt


# Load Gazebo simulation data
data = pd.read_csv('gazebo_platooning_data.csv')

time = data['time']
master_position = data['master_position']
slave_position = data['slave_position']
distance_error = data['distance_error']


# ---------------------------------------------------------
# Plot 1: Master and Slave positions
# ---------------------------------------------------------
plt.figure(figsize=(10, 6))

plt.plot(
    time,
    master_position,
    label='Master Position',
    linewidth=2
)

plt.plot(
    time,
    slave_position,
    label='Slave Position',
    linewidth=2
)

plt.xlabel('Time (s)')
plt.ylabel('Position (m)')
plt.title('Gazebo Platooning - Vehicle Positions')
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig(
    'gazebo_positions.png',
    dpi=300,
    bbox_inches='tight'
)

plt.close()


# ---------------------------------------------------------
# Plot 2: Inter-vehicle distance error
# ---------------------------------------------------------
plt.figure(figsize=(10, 6))

plt.plot(
    time,
    distance_error,
    label='Distance Error',
    linewidth=2
)

plt.axhline(
    y=0.0,
    linestyle='--',
    linewidth=1
)

plt.xlabel('Time (s)')
plt.ylabel('Distance Error (m)')
plt.title('Gazebo Platooning - Distance Error')
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig(
    'gazebo_distance_error.png',
    dpi=300,
    bbox_inches='tight'
)

plt.close()


print('Gazebo plots generated successfully:')
print('  gazebo_positions.png')
print('  gazebo_distance_error.png')

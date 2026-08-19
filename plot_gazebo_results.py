import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv('gazebo_platooning_data.csv')

plt.figure()
plt.plot(data['time'], data['master_position'], label='Master Position')
plt.plot(data['time'], data['slave_position'], label='Slave Position')
plt.xlabel('Time (s)')
plt.ylabel('Position (m)')
plt.title('Gazebo Vehicle Positions')
plt.grid(True)
plt.legend()
plt.savefig('gazebo_positions.png', dpi=300)

plt.figure()
plt.plot(data['time'], data['distance_error'], label='Distance Error')
plt.xlabel('Time (s)')
plt.ylabel('Distance Error (m)')
plt.title('Gazebo Distance Error')
plt.grid(True)
plt.legend()
plt.savefig('gazebo_distance_error.png', dpi=300)

plt.show()

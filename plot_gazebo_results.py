import os
import pandas as pd
import matplotlib.pyplot as plt

data_file = os.path.join(os.getcwd(), 'gazebo_platooning_data.csv')
data = pd.read_csv(data_file)

plt.figure()
plt.plot(data['time'], data['leader_position'], label='Leader Position')
plt.plot(data['time'], data['follower_position'], label='Follower Position')
plt.xlabel('Time (s)')
plt.ylabel('Position (m)')
plt.title('Gazebo Vehicle Positions')
plt.grid(True)
plt.legend()
plt.savefig(os.path.join(os.getcwd(), 'gazebo_positions.png'), dpi=300)

plt.figure()
plt.plot(data['time'], data['distance_error'], label='Distance Error')
plt.xlabel('Time (s)')
plt.ylabel('Distance Error (m)')
plt.title('Gazebo Distance Error')
plt.grid(True)
plt.legend()
plt.savefig(os.path.join(os.getcwd(), 'gazebo_distance_error.png'), dpi=300)

plt.show()

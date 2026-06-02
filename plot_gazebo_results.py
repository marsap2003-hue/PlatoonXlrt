import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv('/home/ms/ros2_ws/gazebo_platooning_data.csv')

plt.figure()
plt.plot(data['time'], data['leader_position'], label='Leader Position')
plt.plot(data['time'], data['follower_position'], label='Follower Position')
plt.xlabel('Time (s)')
plt.ylabel('Position (m)')
plt.title('Gazebo Vehicle Positions')
plt.grid(True)
plt.legend()
plt.savefig('/home/ms/ros2_ws/gazebo_positions.png', dpi=300)

plt.figure()
plt.plot(data['time'], data['distance_error'], label='Distance Error')
plt.xlabel('Time (s)')
plt.ylabel('Distance Error (m)')
plt.title('Gazebo Distance Error')
plt.grid(True)
plt.legend()
plt.savefig('/home/ms/ros2_ws/gazebo_distance_error.png', dpi=300)

plt.show()

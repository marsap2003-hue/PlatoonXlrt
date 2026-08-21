from setuptools import find_packages, setup

import os
from glob import glob

package_name = 'platooning_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (
         os.path.join('share', package_name, 'launch'),
         glob('launch/*.launch.py')
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ms',
    maintainer_email='ms@todo.todo',
    description='ROS2 package for vehicle platooning simulation',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'multi_slave_packetloss = platooning_pkg.multi_slave_packetloss:main',
            'adaptive_slave_node = platooning_pkg.adaptive_slave_node:main',
            'string_master_node = platooning_pkg.string_master_node:main',
            'multi_slave_node = platooning_pkg.multi_slave_node:main',
            'gazebo_master = platooning_pkg.gazebo_master:main',
            'gazebo_slave = platooning_pkg.gazebo_slave:main',
            'data_logger = platooning_pkg.data_logger:main',
        ],
    },
)

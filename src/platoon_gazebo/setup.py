from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'platoon_gazebo'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name]
        ),
        (
            'share/' + package_name,
            ['package.xml']
        ),
        (
            os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')
        ),
        (
            os.path.join('share', package_name, 'worlds'),
            glob('worlds/*.sdf')
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Marios Saparillas',
    maintainer_email='marios.saparillas@example.com',
    description='ROS2 package for Gazebo vehicle platooning simulation',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [],
    },
)

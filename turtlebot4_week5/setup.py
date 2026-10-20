from setuptools import setup
from glob import glob
import os

package_name = 'turtlebot4_week5'
setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
        (os.path.join('share', package_name, 'maps'), glob('maps/*')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*')),
        (os.path.join('share', package_name, 'models'), ['yolov8n.pt']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Student',
    maintainer_email='student@example.com',
    description='TurtleBot 4 autonomous navigation and YOLO perception nodes',
    license='Apache-2.0',
    entry_points={'console_scripts': [
        'goal_sequence = turtlebot4_week5.goal_sequence:main',
        'yolo_detector = turtlebot4_week5.yolo_detector:main',
    ]},
)

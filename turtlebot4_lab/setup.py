from setuptools import setup
from glob import glob
import os

package_name = 'turtlebot4_lab'
setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*')),
        (os.path.join('share', package_name, 'maps'), glob('maps/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Student',
    maintainer_email='student@example.com',
    description='TurtleBot 4 lab launch wrappers',
    license='Apache-2.0',
    entry_points={'console_scripts': [
        'warehouse_survey = turtlebot4_lab.survey_driver:main',
    ]},
)

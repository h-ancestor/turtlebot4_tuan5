from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    upstream = PathJoinSubstitution([FindPackageShare('turtlebot4_navigation'), 'launch', 'localization.launch.py'])
    map_file = PathJoinSubstitution([FindPackageShare('turtlebot4_lab'), 'maps', 'map.yaml'])
    return LaunchDescription([
        DeclareLaunchArgument('map', default_value=map_file),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(upstream), launch_arguments={
            'map': LaunchConfiguration('map'), 'use_sim_time': LaunchConfiguration('use_sim_time')
        }.items()),
    ])

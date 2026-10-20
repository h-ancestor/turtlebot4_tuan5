from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    upstream = PathJoinSubstitution([FindPackageShare('turtlebot4_navigation'), 'launch', 'nav2.launch.py'])
    params = PathJoinSubstitution([FindPackageShare('turtlebot4_navigation'), 'config', 'nav2.yaml'])
    return LaunchDescription([
        DeclareLaunchArgument('params_file', default_value=params),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(upstream), launch_arguments={
            'params_file': LaunchConfiguration('params_file'), 'use_sim_time': LaunchConfiguration('use_sim_time')
        }.items()),
    ])

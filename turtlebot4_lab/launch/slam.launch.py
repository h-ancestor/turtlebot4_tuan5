from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    upstream = PathJoinSubstitution([FindPackageShare('turtlebot4_navigation'), 'launch', 'slam.launch.py'])
    params = PathJoinSubstitution([FindPackageShare('turtlebot4_lab'), 'config', 'slam.yaml'])
    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('params', default_value=params),
        IncludeLaunchDescription(PythonLaunchDescriptionSource(upstream), launch_arguments={
            # Async mode tolerates scan bursts from Ignition better than the
            # exact scan/odom pairing required by the synchronous mapper.
            'use_sim_time': LaunchConfiguration('use_sim_time'), 'sync': 'false',
            'params': LaunchConfiguration('params')
        }.items()),
    ])

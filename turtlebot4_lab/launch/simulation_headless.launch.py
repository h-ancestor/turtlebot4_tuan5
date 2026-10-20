"""Run Ignition Gazebo's server without the IDE's crashing GUI process."""
import os
from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch_ros.actions import Node


def generate_launch_description():
    tb4 = get_package_share_directory('turtlebot4_ignition_bringup')
    lab = get_package_share_directory('turtlebot4_lab')
    create = get_package_share_directory('irobot_create_ignition_bringup')
    description = get_package_share_directory('turtlebot4_description')
    create_description = get_package_share_directory('irobot_create_description')
    world = LaunchConfiguration('world')
    model = LaunchConfiguration('model')
    resources = ':'.join([
        os.path.join(lab, 'worlds'),
        os.path.join(tb4, 'worlds'),
        os.path.join(create, 'worlds'),
        str(Path(description).parent.resolve()),
        str(Path(create_description).parent.resolve()),
    ])
    server = ExecuteProcess(
        cmd=['ign', 'gazebo', '-s', '--headless-rendering', '-r', '-v', '3',
             PathJoinSubstitution([lab, 'worlds', PythonExpression(["'", world, ".sdf'"])])],
        output='screen',
    )
    clock = Node(
        package='ros_gz_bridge', executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock'],
        output='screen',
    )
    spawn = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(lab, 'launch', 'turtlebot4_spawn_lab.launch.py')),
        launch_arguments={
            'model': model,
            'rviz': 'false',
            'use_sim_time': 'true',
            'spawn_dock': LaunchConfiguration('spawn_dock'),
        }.items(),
    )
    return LaunchDescription([
        DeclareLaunchArgument('world', default_value='warehouse'),
        DeclareLaunchArgument('model', default_value='lite', choices=['lite', 'standard']),
        DeclareLaunchArgument('spawn_dock', default_value='false', choices=['true', 'false']),
        SetEnvironmentVariable('IGN_GAZEBO_RESOURCE_PATH', resources),
        SetEnvironmentVariable('ROS_LOCALHOST_ONLY', '1'),
        SetEnvironmentVariable('IGN_GAZEBO_SYSTEM_PLUGIN_PATH', '/opt/ros/humble/lib:/usr/lib/x86_64-linux-gnu/ign-gazebo-6/plugins'),
        server,
        clock,
        spawn,
    ])

"""Run the patched headless Gazebo server with RViz for the TurtleBot 4."""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable, UnsetEnvironmentVariable
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    lab_share = FindPackageShare('turtlebot4_lab')
    viz_share = FindPackageShare('turtlebot4_viz')
    rviz_config = LaunchConfiguration('rviz_config')
    simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([lab_share, 'launch', 'simulation_headless.launch.py'])
        ),
        launch_arguments={
            'world': LaunchConfiguration('world'),
            'model': LaunchConfiguration('model'),
            'spawn_dock': LaunchConfiguration('spawn_dock'),
        }.items(),
    )
    rviz = Node(
        package='rviz2', executable='rviz2', name='rviz2', output='screen',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': True}],
        remappings=[('/tf', 'tf'), ('/tf_static', 'tf_static')],
        condition=IfCondition(LaunchConfiguration('rviz')),
    )
    return LaunchDescription([
        # Avoid IDE-injected Snap GTK settings that can make RViz abort.
        UnsetEnvironmentVariable('GTK_PATH'),
        UnsetEnvironmentVariable('GTK_EXE_PREFIX'),
        UnsetEnvironmentVariable('GTK_MODULES'),
        UnsetEnvironmentVariable('GTK_IM_MODULE_FILE'),
        UnsetEnvironmentVariable('GTK_IM_MODULE'),
        UnsetEnvironmentVariable('GSETTINGS_SCHEMA_DIR'),
        SetEnvironmentVariable('XDG_DATA_DIRS', '/usr/share/ubuntu:/usr/share:/usr/local/share'),
        DeclareLaunchArgument('world', default_value='warehouse'),
        DeclareLaunchArgument('model', default_value='lite', choices=['lite', 'standard']),
        DeclareLaunchArgument('spawn_dock', default_value='false', choices=['true', 'false']),
        DeclareLaunchArgument('rviz', default_value='true', choices=['true', 'false']),
        DeclareLaunchArgument(
            'rviz_config',
            default_value=PathJoinSubstitution([viz_share, 'rviz', 'robot.rviz']),
        ),
        simulation,
        rviz,
    ])

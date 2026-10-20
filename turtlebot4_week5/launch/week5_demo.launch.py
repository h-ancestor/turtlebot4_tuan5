"""Start the warehouse simulator, AMCL/Nav2, sequential goals and YOLO."""
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    SetEnvironmentVariable,
    TimerAction,
    UnsetEnvironmentVariable,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    lab_share = FindPackageShare('turtlebot4_lab')
    week5_share = FindPackageShare('turtlebot4_week5')
    map_file = LaunchConfiguration('map')
    world = LaunchConfiguration('world')
    model = LaunchConfiguration('model')
    start_goals = LaunchConfiguration('start_goals')
    start_yolo = LaunchConfiguration('start_yolo')
    initial_x = LaunchConfiguration('initial_x')
    initial_y = LaunchConfiguration('initial_y')
    initial_yaw = LaunchConfiguration('initial_yaw')
    image_topic = LaunchConfiguration('image_topic')
    model_path = LaunchConfiguration('model_path')
    inference_hz = LaunchConfiguration('inference_hz')
    image_size = LaunchConfiguration('image_size')

    simulator = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([lab_share, 'launch', 'simulation.launch.py'])
        ),
        launch_arguments={
            'world': world,
            'model': model,
            'rviz': 'false',
        }.items(),
    )
    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([week5_share, 'launch', 'localization_navigation.launch.py'])
        ),
        launch_arguments={'map': map_file, 'use_sim_time': 'true'}.items(),
    )
    goal_node = Node(
        package='turtlebot4_week5',
        executable='goal_sequence',
        name='goal_sequence',
        output='screen',
        parameters=[{
            'initial_pose_enabled': True,
            'initial_x': initial_x,
            'initial_y': initial_y,
            'initial_yaw': initial_yaw,
        }],
        condition=IfCondition(start_goals),
    )
    yolo_node = Node(
        package='turtlebot4_week5',
        executable='yolo_detector',
        name='turtlebot4_yolo_detector',
        output='screen',
        parameters=[{
            'model_path': model_path,
            'image_topic': image_topic,
            'annotated_topic': '/yolo/image',
            'show_window': False,
            'inference_hz': inference_hz,
            'image_size': image_size,
        }],
        condition=IfCondition(start_yolo),
    )
    rviz_node = Node(
        package='rviz2', executable='rviz2', name='rviz', output='screen',
        arguments=['-d', PathJoinSubstitution([week5_share, 'rviz', 'week5.rviz'])],
        parameters=[{'use_sim_time': True}],
        remappings=[('/tf', 'tf'), ('/tf_static', 'tf_static')],
    )

    return LaunchDescription([
        UnsetEnvironmentVariable('GTK_PATH'),
        UnsetEnvironmentVariable('GTK_EXE_PREFIX'),
        UnsetEnvironmentVariable('GTK_MODULES'),
        UnsetEnvironmentVariable('GTK_IM_MODULE_FILE'),
        UnsetEnvironmentVariable('GTK_IM_MODULE'),
        UnsetEnvironmentVariable('GSETTINGS_SCHEMA_DIR'),
        SetEnvironmentVariable('XDG_DATA_DIRS', '/usr/share/ubuntu:/usr/share:/usr/local/share'),
        SetEnvironmentVariable('ROS_LOCALHOST_ONLY', '1'),
        DeclareLaunchArgument('world', default_value='warehouse'),
        DeclareLaunchArgument('model', default_value='lite'),
        DeclareLaunchArgument(
            'map',
            default_value=PathJoinSubstitution([week5_share, 'maps', 'warehouse_slam.yaml']),
            description='Ưu tiên truyền bản đồ do bạn tự quét bằng SLAM.'),
        DeclareLaunchArgument('start_goals', default_value='false'),
        DeclareLaunchArgument('start_yolo', default_value='false'),
        DeclareLaunchArgument('initial_x', default_value='0.0'),
        DeclareLaunchArgument('initial_y', default_value='0.0'),
        DeclareLaunchArgument('initial_yaw', default_value='0.0'),
        DeclareLaunchArgument('image_topic', default_value='/oakd/rgb/preview/image_raw'),
        DeclareLaunchArgument(
            'model_path',
            default_value=PathJoinSubstitution([
                week5_share, 'models', 'yolov8n.pt']),
        ),
        DeclareLaunchArgument('inference_hz', default_value='0.5'),
        DeclareLaunchArgument('image_size', default_value='320'),
        simulator,
        rviz_node,
        # Give Gazebo, TF, sensor bridges, and RViz time to settle before AMCL/Nav2.
        TimerAction(period=15.0, actions=[localization]),
        # Keep autonomy opt-in: verify /scan and set an accurate initial pose first.
        TimerAction(period=28.0, actions=[goal_node, yolo_node]),
    ])

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'model_path',
            default_value=PathJoinSubstitution([
                FindPackageShare('turtlebot4_week5'), 'models', 'yolov8n.pt']),
        ),
        DeclareLaunchArgument('image_topic', default_value='/oakd/rgb/preview/image_raw'),
        DeclareLaunchArgument('annotated_topic', default_value='/yolo/image'),
        DeclareLaunchArgument('show_window', default_value='true'),
        DeclareLaunchArgument('inference_hz', default_value='0.5'),
        DeclareLaunchArgument('image_size', default_value='320'),
        Node(
            package='turtlebot4_week5', executable='yolo_detector', output='screen',
            parameters=[{
                'model_path': LaunchConfiguration('model_path'),
                'image_topic': LaunchConfiguration('image_topic'),
                'annotated_topic': LaunchConfiguration('annotated_topic'),
                'show_window': LaunchConfiguration('show_window'),
                'inference_hz': LaunchConfiguration('inference_hz'),
                'image_size': LaunchConfiguration('image_size'),
            }],
        ),
    ])

"""Send an ordered list of map-frame poses to Nav2 using Simple Commander."""
import math

import rclpy
import yaml
from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from rclpy.duration import Duration


def make_pose(navigator, x, y, yaw, frame):
    pose = PoseStamped()
    pose.header.frame_id = frame
    pose.header.stamp = navigator.get_clock().now().to_msg()
    pose.pose.position.x = float(x)
    pose.pose.position.y = float(y)
    pose.pose.orientation.z = math.sin(float(yaw) / 2.0)
    pose.pose.orientation.w = math.cos(float(yaw) / 2.0)
    return pose


def main(args=None):
    rclpy.init(args=args)
    nav = BasicNavigator()
    nav.declare_parameter('frame_id', 'map')
    nav.declare_parameter('goals_file', '')
    nav.declare_parameter('initial_x', 0.0)
    nav.declare_parameter('initial_y', 0.0)
    nav.declare_parameter('initial_yaw', 0.0)
    nav.declare_parameter('initial_pose_enabled', True)
    frame = nav.get_parameter('frame_id').value
    goals_path = nav.get_parameter('goals_file').value
    if not goals_path:
        goals_path = get_package_share_directory('turtlebot4_week5') + '/config/goals.yaml'
    with open(goals_path, encoding='utf-8') as f:
        goals = yaml.safe_load(f)['waypoints']
    if len(goals) < 3:
        nav.get_logger().fatal('goals_file must contain at least three waypoints')
        nav.destroy_node()
        rclpy.shutdown()
        return

    if nav.get_parameter('initial_pose_enabled').value:
        initial = make_pose(nav,
                            nav.get_parameter('initial_x').value,
                            nav.get_parameter('initial_y').value,
                            nav.get_parameter('initial_yaw').value,
                            frame)
        nav.setInitialPose(initial)
    nav.get_logger().info('Waiting for Nav2 lifecycle nodes and AMCL...')
    nav.waitUntilNav2Active(localizer='amcl')

    for index, goal in enumerate(goals, start=1):
        pose = make_pose(nav, goal['x'], goal['y'], goal.get('yaw', 0.0), frame)
        nav.get_logger().info(
            f'Goal {index}/{len(goals)}: x={goal["x"]:.2f}, y={goal["y"]:.2f}, '
            f'yaw={goal.get("yaw", 0.0):.2f} in {frame}')
        nav.goToPose(pose)
        while not nav.isTaskComplete():
            feedback = nav.getFeedback()
            if feedback and feedback.navigation_time:
                if Duration.from_msg(feedback.navigation_time).nanoseconds > 600_000_000_000:
                    nav.get_logger().error(f'Goal {index} timed out; canceling navigation')
                    nav.cancelTask()
                    break
            rclpy.spin_once(nav, timeout_sec=0.1)
        result = nav.getResult()
        if result == TaskResult.SUCCEEDED:
            nav.get_logger().info(f'Goal {index} succeeded')
        elif result == TaskResult.CANCELED:
            nav.get_logger().error(f'Goal {index} was canceled; stopping sequence')
            break
        else:
            nav.get_logger().error(f'Goal {index} failed; stopping sequence')
            break

    nav.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

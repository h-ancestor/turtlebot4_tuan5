"""Slow odometry-guided warehouse survey for the SLAM exercise."""
import math
import time

import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node


def clamp(value, low, high):
    return max(low, min(high, value))


class SurveyDriver(Node):
    def __init__(self):
        super().__init__('warehouse_survey_driver')
        self.pose = None
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.create_subscription(Odometry, '/odom', self.on_odom, 10)

    def on_odom(self, msg):
        p = msg.pose.pose.position
        q = msg.pose.pose.orientation
        yaw = math.atan2(2.0 * (q.w * q.z + q.x * q.y),
                         1.0 - 2.0 * (q.y * q.y + q.z * q.z))
        self.pose = (p.x, p.y, yaw)

    def stop(self):
        self.publisher.publish(Twist())

    def run_route(self):
        deadline = time.monotonic() + 600.0
        while rclpy.ok() and self.pose is None and time.monotonic() < deadline:
            rclpy.spin_once(self, timeout_sec=0.1)
        if self.pose is None:
            raise RuntimeError('No /odom received')

        # Survey the central aisle, then add a slow, broad loop through the
        # clear southern cross-aisle (around y=-5 m). The route stays east of
        # the person/shelf cluster near x=0, y=-1..-2 and returns through the
        # already mapped area to close the loop.
        waypoints = [
            (5.0, 0.0), (5.0, 6.0), (-5.0, 6.0), (-5.0, 0.0), (0.0, 0.0),
            (6.0, 0.0), (6.0, -5.0), (-6.0, -5.0), (-6.0, 0.0),
            (-5.0, 6.0), (0.0, 6.0), (5.0, 6.0), (5.0, 0.0), (0.0, 0.0),
        ]
        for index, (tx, ty) in enumerate(waypoints, 1):
            segment_deadline = time.monotonic() + 400.0
            self.get_logger().info(f'Survey waypoint {index}/{len(waypoints)}: ({tx:.1f}, {ty:.1f})')
            while rclpy.ok() and time.monotonic() < segment_deadline:
                rclpy.spin_once(self, timeout_sec=0.03)
                if self.pose is None:
                    continue
                x, y, yaw = self.pose
                dx, dy = tx - x, ty - y
                distance = math.hypot(dx, dy)
                if distance < 0.18:
                    break
                desired = math.atan2(dy, dx)
                error = math.atan2(math.sin(desired - yaw), math.cos(desired - yaw))
                cmd = Twist()
                cmd.angular.z = clamp(0.9 * error, -0.25, 0.25)
                cmd.linear.x = 0.12 * max(0.0, math.cos(error))
                self.publisher.publish(cmd)
            else:
                raise RuntimeError(f'Could not reach waypoint ({tx}, {ty})')
            self.stop()
            for _ in range(5):
                rclpy.spin_once(self, timeout_sec=0.05)
        self.stop()


def main():
    rclpy.init()
    node = SurveyDriver()
    try:
        node.run_route()
    finally:
        node.stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

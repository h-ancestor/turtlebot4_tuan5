"""Subscribe to the TurtleBot RGB preview, run Ultralytics YOLO, publish annotated frames."""
import time

import cv2
import rclpy
from cv_bridge import CvBridge
from ament_index_python.packages import get_package_share_directory
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image


class YoloDetector(Node):
    def __init__(self, model):
        super().__init__('turtlebot4_yolo_detector')
        self.declare_parameter('image_topic', '/oakd/rgb/preview/image_raw')
        self.declare_parameter('annotated_topic', '/yolo/image')
        self.declare_parameter('confidence', 0.35)
        self.declare_parameter('inference_hz', 0.5)
        self.declare_parameter('image_size', 320)
        self.declare_parameter('show_window', True)
        self.bridge = CvBridge()
        self.model = model
        self.last_inference = 0.0
        self.image_sub = self.create_subscription(
            Image, self.get_parameter('image_topic').value, self.on_image,
            qos_profile_sensor_data)
        self.image_pub = self.create_publisher(
            Image, self.get_parameter('annotated_topic').value, 5)
        self.get_logger().info(
            f"YOLO ready; input={self.get_parameter('image_topic').value}, "
            f"output={self.get_parameter('annotated_topic').value}")

    def on_image(self, msg):
        now = time.monotonic()
        hz = max(0.1, float(self.get_parameter('inference_hz').value))
        if now - self.last_inference < 1.0 / hz:
            return
        self.last_inference = now
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            result = self.model.predict(
                source=frame, conf=float(self.get_parameter('confidence').value),
                imgsz=int(self.get_parameter('image_size').value), device='cpu',
                verbose=False)[0]
            annotated = result.plot()
            out = self.bridge.cv2_to_imgmsg(annotated, encoding='bgr8')
            out.header = msg.header
            self.image_pub.publish(out)
            if result.boxes is not None:
                for box in result.boxes:
                    class_id = int(box.cls.item())
                    confidence = float(box.conf.item())
                    label = self.model.names.get(class_id, str(class_id))
                    self.get_logger().info(f'detected {label} confidence={confidence:.2f}')
            if self.get_parameter('show_window').value:
                cv2.imshow('TurtleBot 4 YOLO', annotated)
                cv2.waitKey(1)
        except Exception as exc:
            self.get_logger().error(f'Image inference failed: {exc}')

    def destroy_node(self):
        cv2.destroyAllWindows()
        super().destroy_node()


def main(args=None):
    # Keep CPU inference from starving Nav2's controller and lifecycle heartbeat.
    import os
    os.environ.setdefault('OMP_NUM_THREADS', '1')
    os.environ.setdefault('MKL_NUM_THREADS', '1')
    rclpy.init(args=args)
    bootstrap = Node('yolo_model_loader')
    bootstrap.declare_parameter('model_path', 'yolov8n.pt')
    model_path = bootstrap.get_parameter('model_path').value
    if model_path == 'yolov8n.pt':
        bundled_weights = get_package_share_directory('turtlebot4_week5') + '/models/yolov8n.pt'
        if __import__('os').path.isfile(bundled_weights):
            model_path = bundled_weights
    try:
        import torch
        torch.set_num_threads(1)
        torch.set_num_interop_threads(1)
        from ultralytics import YOLO
        model = YOLO(model_path)
    except Exception as exc:
        bootstrap.get_logger().fatal(
            f'Cannot load Ultralytics model {model_path!r}: {exc}. '
            'Install ultralytics in the same Python environment and ensure weights are available.')
        bootstrap.destroy_node()
        rclpy.shutdown()
        return
    bootstrap.destroy_node()
    node = YoloDetector(model)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

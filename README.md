# TurtleBot 4 – Bài thực hành 05

Workspace ROS 2 Humble để chạy TurtleBot 4 trong Gazebo warehouse, nạp map SLAM tuần 4, định vị bằng AMCL, gửi tuần tự ba goal tới Nav2 bằng code và chạy YOLO trên ảnh camera OAK-D.

## Nội dung

- `turtlebot4_lab/`: launch/config/world của simulation và SLAM.
- `turtlebot4_week5/`: node `goal_sequence`, node `yolo_detector`, launch, cấu hình goal, RViz và model YOLOv8n.
- `maps/map.yaml`, `maps/map.pgm`: map được lưu từ SLAM Toolbox; 560×472 px, resolution 0.05 m, khảo sát aisle trung tâm, chưa phủ toàn bộ warehouse.
- `docs/`: báo cáo tuần 5 và ảnh minh họa. Bản DOCX có thể sửa; sau khi điền link video/repository, xuất lại PDF.

## Cài đặt (Ubuntu 22.04, ROS 2 Humble)

```bash
sudo apt update
sudo apt install ros-humble-desktop ros-humble-turtlebot4-simulator \
  ros-humble-turtlebot4-navigation ros-humble-nav2-simple-commander \
  ros-humble-cv-bridge ros-humble-slam-toolbox python3-opencv python3-yaml
python3 -m pip install ultralytics
```

## Build

Tại thư mục gốc repository:

```bash
source /opt/ros/humble/setup.bash
colcon build --base-paths turtlebot4_lab turtlebot4_week5 --symlink-install
source install/setup.bash
```

## Chạy simulation, localization, Nav2 và YOLO

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch turtlebot4_week5 week5_demo.launch.py \
  map:="$(pwd)/maps/map.yaml" start_goals:=false start_yolo:=true \
  inference_hz:=0.5 image_size:=320
```

Sau khi RViz xác nhận map/scan/pose khớp và Nav2 báo active, chạy chuỗi goal bằng node:

```bash
ros2 run turtlebot4_week5 goal_sequence --ros-args \
  -p initial_pose_enabled:=true -p initial_x:=0.0 \
  -p initial_y:=0.0 -p initial_yaw:=0.0
```

Ba waypoint hiện cấu hình trong `turtlebot4_week5/config/goals.yaml`: (5, 0, 0), (5, 6, 1.5708), (-5, 6, 3.1416), đơn vị mét/radian trong frame `map`. Chỉ chạy autonomy sau khi kiểm tra đúng world và initial pose.

Topic chính: `/scan`, `/odom`, `/cmd_vel`, `/map`, `/amcl_pose`, `/oakd/rgb/preview/image_raw`, `/yolo/image`; Nav2 action: `/navigate_to_pose`.

## Kết quả và giới hạn

Trong lượt chạy đã ghi nhận, node điều hướng lần lượt nhận `SUCCEEDED` ở cả ba goal; AMCL tại Goal 3 khoảng (-4.74, 6.05), cách tọa độ mục tiêu khoảng 0.27 m. YOLOv8n đã phát hiện class `person` trên ảnh mô phỏng; ảnh annotate nằm trong `docs/tuan05_yolo_detection.png`. Map chỉ bao phủ tuyến khảo sát aisle trung tâm; Nav2 có thể mất vài phút để khởi tạo trên máy yếu.

Video demo sẽ được chia sẻ bằng Google Drive theo yêu cầu môn học, không đặt trong repository này. Thêm link Drive tại đây: **[Video demo – cập nhật link]**.

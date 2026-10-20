# TurtleBot 4 – Bài thực hành 05

Package ROS 2 Python cho AMCL/Nav2, tuần tự gửi ít nhất ba goal bằng Nav2 Simple Commander và nhận diện ảnh RGB bằng Ultralytics YOLO.

## Nội dung package

- `goal_sequence`: đọc `config/goals.yaml`, thiết lập initial pose nếu được bật, đợi AMCL/Nav2 active, gửi lần lượt các pose trong frame `map` bằng `BasicNavigator.goToPose()` và dừng chuỗi nếu một goal thất bại.
- `yolo_detector`: subscribe `sensor_msgs/msg/Image`, đổi ảnh sang BGR bằng `cv_bridge`, chạy YOLO, ghi class/độ tin cậy ra terminal và publish ảnh annotate lên `/yolo/image`.
- `localization_navigation.launch.py`: khởi chạy localization (AMCL/map server) trước rồi mới khởi chạy Nav2.
- `week5_demo.launch.py`: chạy simulator warehouse, localization/Nav2, goal sequence và YOLO; bật tuần tự goal/detector bằng tham số launch.
- `rviz/week5.rviz`: RViz hiển thị bản đồ, LiDAR, robot model, camera OAK-D RGB và ảnh kết quả YOLO.
- `maps/warehouse_slam.*`: bản đồ warehouse vừa lưu từ SLAM Toolbox trong tuyến khảo sát; dùng làm mặc định cho localization/Nav2.
- `maps/warehouse_reference.*`: bản đồ upstream cài cùng TurtleBot 4, giữ làm tham chiếu.

## Cài dependency

Trên Ubuntu 22.04 + ROS 2 Humble đã cài TurtleBot 4 Simulation:

```bash
sudo apt update
sudo apt install ros-humble-turtlebot4-navigation ros-humble-nav2-simple-commander \
  ros-humble-cv-bridge python3-opencv python3-yaml
python3 -m pip install ultralytics
```

YOLO mặc định dùng `yolov8n.pt`; Ultralytics cần tải weights lần đầu nếu file chưa có. Hãy dùng Python cùng môi trường ROS đã source để import được `cv_bridge`. Nếu máy offline, có thể truyền đường dẫn tới weights đã tải sẵn bằng `model_path`.

## Build

Chạy từ thư mục `bài thực hành 04`:

```bash
source /opt/ros/humble/setup.bash
colcon build --base-paths turtlebot4_lab turtlebot4_week5 --symlink-install
source install/setup.bash
```

## Chạy từng bước (khuyến nghị)

Terminal 1 – simulator. Có thể dùng `rviz:=false` khi máy không hỗ trợ Gazebo/RViz GUI:

```bash
ros2 launch turtlebot4_lab simulation.launch.py world:=warehouse model:=lite rviz:=true
```

Terminal 2 – AMCL và Nav2. Thay map mặc định bằng YAML do bạn tự quét nếu đã có map hợp lệ:

```bash
ros2 launch turtlebot4_week5 localization_navigation.launch.py \
  map:=/absolute/path/to/your/map.yaml use_sim_time:=true
```

Terminal 3 – sau khi xác nhận bản đồ và initial pose khớp robot trong Gazebo, chạy chuỗi goal:

```bash
ros2 run turtlebot4_week5 goal_sequence --ros-args \
  -p initial_pose_enabled:=true -p initial_x:=0.0 -p initial_y:=0.0 -p initial_yaw:=0.0
```

Initial pose mặc định là `(0, 0, 0)` cho robot spawn gần gốc trong world warehouse; thay theo pose thực tế nếu cần. Các waypoint trong `config/goals.yaml` đã được chạy trên map SLAM kèm package.

Terminal 4 – chạy detector (cửa sổ OpenCV bật mặc định khi chạy node trực tiếp):

```bash
ros2 launch turtlebot4_week5 yolo.launch.py show_window:=true
```

Mặc định detector giới hạn inference ở `0.5 Hz`, ảnh vào mô hình được thu nhỏ tới `320 px`, và PyTorch dùng một CPU thread để tránh làm trễ controller Nav2. Có thể tăng `inference_hz` hoặc `image_size` trên máy đủ mạnh.

Topic camera mặc định `/oakd/rgb/preview/image_raw`. Nếu topic thực tế khác, truyền `image_topic:=/topic/camera`. Xem ảnh annotate tại `/yolo/image`; nếu chạy headless, đặt `show_window:=false`.

## Chạy tiện ích gộp

Launch gộp khởi simulator, đợi 15 giây rồi khởi AMCL/Nav2. Các tác vụ chuyển động và YOLO mặc định tắt để người chạy có thể xác nhận map/pose và dependency trước:

```bash
ros2 launch turtlebot4_week5 week5_demo.launch.py \
  map:=/absolute/path/to/your/map.yaml start_goals:=false start_yolo:=false
```

Chỉ sau khi kiểm tra laser scan khớp tường trên map và cài được YOLO cùng weights, có thể bật:

```bash
ros2 launch turtlebot4_week5 week5_demo.launch.py \
  map:=/absolute/path/to/your/map.yaml start_goals:=true start_yolo:=true \
  initial_x:=0.0 initial_y:=0.0 initial_yaw:=0.0
```

Đã kiểm chứng chuỗi ba waypoint trên map SLAM với YOLO chạy đồng thời bằng cấu hình nhẹ sau:

```bash
ros2 launch turtlebot4_week5 week5_demo.launch.py \
  start_goals:=true start_yolo:=true inference_hz:=0.5 image_size:=320
```

Launch mặc định dùng `maps/warehouse_slam.yaml`; robot được spawn gần `(0, 0, 0)`. Kiểm tra pose và các waypoint trên RViz trước khi chạy autonomy.

## Các topic/action chính

- Sensor/robot: `/scan`, `/odom`, `/tf`, `/tf_static`, camera RGB và `/cmd_vel`.
- Localization: `/map`, `/amcl_pose`, `/initialpose`.
- Navigation: action `/navigate_to_pose`; costmap và path do Nav2 quản lý; `goal_sequence` gửi goal qua Simple Commander.
- YOLO: input `/oakd/rgb/preview/image_raw`, output ảnh annotate `/yolo/image`.

## Trạng thái kiểm thử thực tế và giới hạn

- Đã chạy Ultralytics YOLOv8n trên camera RGB mô phỏng. Detector in nhãn vật thể và publish ảnh bounding box lên `/yolo/image`.
- SLAM Toolbox đã tạo map 560×472, resolution 0.05 m/pixel, từ tuyến survey năm waypoint. Robot thực sự di chuyển trong Gazebo.
- Hai lượt cuối của chuỗi ba waypoint hoàn tất bằng code khi Nav2 và AMCL active; cả ba action trả `SUCCEEDED`. Ở Goal 3 AMCL khoảng `(-4.74, 6.05)` so với target `(-5, 6)`, sai khác tâm khoảng 0.27 m.
- Chuỗi ba goal hoàn tất khi YOLO chạy đồng thời ở `0.5 Hz`, `imgsz=320`. Cấu hình YOLO nặng trước đó làm controller trễ heartbeat, nên giữ thiết lập throttled khi demo trên CPU.
- Tuyến SLAM khảo sát aisle trung tâm, chưa bao phủ toàn bộ warehouse; bản đồ còn một số nhiễu từ LiDAR/world. Chưa kiểm chứng navigation ở mọi vùng của world hoặc trên môi trường khác. Lifecycle/Nav2 cần vài phút để khởi tạo trên máy này.
- Báo cáo tuần 5: `../docs/bao-cao-tuan-05.pdf` và DOCX cùng tên. Video quay RViz 5:07: `../docs/tuan05_demo.webm`; ảnh minh họa nằm trong thư mục `../docs/`.

# Nguồn bản đồ hiện tại

`map.yaml` và `map.pgm` được lưu từ topic `/map` của SLAM Toolbox sau khi robot mô phỏng tự chạy tuyến survey năm waypoint trong world `warehouse` của TurtleBot 4. Bản đồ có độ phân giải 0.05 m/pixel, kích thước 560×472 pixel.

Map được tạo tự động bằng SLAM trong môi trường warehouse; vùng khảo sát tập trung quanh aisle trung tâm, chưa bao phủ toàn bộ warehouse. Tệp map lỗi cũ được giữ tại `map_invalid_1pixel.yaml` và `map_invalid_1pixel.pgm` để lưu dấu kết quả lần chạy trước.

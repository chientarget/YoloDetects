# Hệ Thống Phát Hiện và Nhận Diện Đối Tượng Trong Video Thời Gian Thực

## Giới Thiệu
Dự án này được phát triển như một phần của môn học Xử Lý Ảnh và Thị Giác Máy Tính. Hệ thống tập trung vào việc phát hiện và nhận diện đối tượng trong video thời gian thực sử dụng các mô hình YOLO (You Only Look Once).
- Dự án được thực hiện bởi nhóm sinh viên **Nhóm 5 - CNTT12.10.2** trường Đại học Công Nghệ Đông Á 
- Môn học: Xử Lý Ảnh và Thị Giác Máy Tính
- Giảng viên hướng dẫn: **LƯƠNG THỊ HỒNG LAN**
- Ngày báo cáo: 07/12/2024
## Thành Viên Nhóm
- **Nguyễn Huy Chiến**
- Trần Tùng Dương
- Lê Đức Anh
- Đỗ Thị Vân

## Slide Thuyết Trình
[Link Slide Canva](https://www.canva.com/design/DAGYhvnY3ZU/LLYQhK-_-TxT7PejhG_3xg/edit)

## Tính Năng Chính
- Phát hiện đối tượng thời gian thực qua webcam
- Hỗ trợ xử lý video từ file
- Tự động tải và phát hiện video từ thư mục
- Hỗ trợ nhiều mô hình YOLO (v2, v3, v4)
- Giao diện người dùng thân thiện với PyQt6
- Tùy chỉnh ngưỡng tin cậy và NMS
- Hiển thị kết quả với khung bao và nhãn
- Cache frame để tối ưu hiệu suất

## Công Nghệ Sử Dụng
- **Ngôn ngữ:** Python
- **Framework AI:** YOLO (You Only Look Once)
- **Thư viện chính:**
  - OpenCV
  - PyQt6
  - PyTorch
  - NumPy
- **Mô hình:** YOLOv2, YOLOv3, YOLOv4

## Kiến Trúc Hệ Thống
1. **Module Giao Diện (UI):**
   - Quản lý tương tác người dùng
   - Hiển thị video và kết quả phát hiện
   - Điều khiển luồng xử lý

2. **Module Phát Hiện:**
   - Xử lý frame
   - Áp dụng mô hình YOLO
   - Lọc và tối ưu kết quả

3. **Module Xử Lý Video:**
   - Đọc và xử lý video
   - Cache frame
   - Quản lý luồng dữ liệu

## Đối Tượng Phát Hiện
- Con người và phương tiện giao thông
- Biển báo và thiết bị giao thông
- Đồ nội thất và thiết bị gia dụng
- Động vật
- Đồ dùng cá nhân
- Dụng cụ thể thao
- Đồ dùng nhà bếp và thực phẩm
- Thiết bị điện tử

## Kết Quả Đạt Được
- Phát hiện đối tượng chính xác với độ tin cậy cao
- Xử lý thời gian thực mượt mà
- Giao diện người dùng trực quan
- Hỗ trợ đa dạng nguồn video
- Tối ưu hiệu suất với cache


## Liên Hệ
- Email: chientarget@gmail.com
- GitHub: [GitHub Chientarget](https://github.com/chientarget)

---
*Dự án này được phát triển cho mục đích học tập và nghiên cứu. Trích nguồn khi sử dụng dự án này.
*

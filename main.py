import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QComboBox, QPushButton, QFileDialog, QListWidget,
                             QFrame, QSplitter, QScrollArea, QStyleFactory, QListWidgetItem, QSlider)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap, QPalette, QColor, QFont
from config import YOLO_CONFIGS, CLASSES
from detector import YOLODetector, DetectionThread
from utils import draw_detections
import os


class ModernButton(QPushButton):
    def __init__(self, text, color="#2196F3"):
        super().__init__(text)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: none;                                                                                                      
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.adjust_color(color, 1.1)};
            }}
            QPushButton:pressed {{
                background-color: {self.adjust_color(color, 0.9)};
            }}
        """)

    def adjust_color(self, color, factor):
        # Hàm điều chỉnh màu sắc
        color = color.lstrip('#')
        r = int(min(255, int(color[0:2], 16) * factor))
        g = int(min(255, int(color[2:4], 16) * factor))
        b = int(min(255, int(color[4:6], 16) * factor))
        return f"#{r:02x}{g:02x}{b:02x}"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YOLO Object Detection System")
        self.setGeometry(100, 100, 1200, 800)

        # Khởi tạo dict màu cho các đối tượng ngay từ đầu
        self.object_colors = {}
        for class_name in CLASSES:
            r = np.random.randint(100, 256)
            g = np.random.randint(100, 256)
            b = np.random.randint(100, 256)
            self.object_colors[class_name.lower()] = {
                'rgb': (r, g, b),
                'hex': f"#{r:02x}{g:02x}{b:02x}"
            }

        self.setup_ui()
        self.apply_styles()

        # Tự động load videos khi khởi động
        self.auto_load_videos()

    def setup_ui(self):
        # Tạo widget chính
        main_widget = QWidget()
        main_layout = QHBoxLayout()

        # Panel điều khiển bên trái
        control_panel = self.create_control_panel()

        # Khu vực hiển thị chính
        display_area = self.create_display_area()

        # Panel thông tin bên phải
        info_panel = self.create_info_panel()

        # Thêm các panel vào splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(control_panel)
        splitter.addWidget(display_area)
        splitter.addWidget(info_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 4)
        splitter.setStretchFactor(2, 1)

        main_layout.addWidget(splitter)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def create_control_panel(self):
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout()

        # Tiêu đề panel
        title = QLabel("Control Panel")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        # Model selection
        layout.addWidget(QLabel("YOLO Model:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["YOLOv2", "YOLOv3", "YOLOv4", "YOLOv5"])
        self.model_combo.setStyleSheet("QComboBox { padding: 5px; }")
        layout.addWidget(self.model_combo)

        # Input source
        layout.addWidget(QLabel("Input Source:"))
        self.input_combo = QComboBox()
        self.input_combo.addItems(["Video", "Image", "Camera"])
        layout.addWidget(self.input_combo)

        self.input_button = ModernButton("Browse")
        self.input_button.clicked.connect(self.browse_input)
        layout.addWidget(self.input_button)

        # Object selection
        layout.addWidget(QLabel("Detection Objects:"))
        self.object_list = QListWidget()
        self.object_list.addItems([class_name.title() for class_name in CLASSES])
        self.object_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        layout.addWidget(self.object_list)

        # Control buttons
        self.start_button = ModernButton("Start Detection", "#4CAF50")
        self.stop_button = ModernButton("Stop Detection", "#f44336")
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)

        self.start_button.clicked.connect(self.start_detection)
        self.stop_button.clicked.connect(self.stop_detection)

        # Thêm nút Camera Detection
        self.camera_button = ModernButton("Camera Detection", "#9C27B0")  # Màu tím
        self.camera_button.clicked.connect(self.start_camera_detection)
        layout.addWidget(self.camera_button)

        layout.addStretch()
        panel.setLayout(layout)
        return panel

    def create_display_area(self):
        display_frame = QFrame()
        display_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout()

        # Tiêu đề
        title = QLabel("Detection View")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Khu vực hiển thị
        self.display_label = QLabel()
        self.display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display_label.setMinimumSize(640, 480)
        self.display_label.setStyleSheet("QLabel { background-color: #1e1e1e; }")

        scroll_area = QScrollArea()
        scroll_area.setWidget(self.display_label)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        self.video_slider = QSlider(Qt.Orientation.Horizontal)
        self.video_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #3d3d3d;
                height: 8px;
                background: #2d2d2d;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #4CAF50;
                border: 1px solid #3d3d3d;
                width: 18px;
                margin: -2px 0;
                border-radius: 4px;
            }
        """)
        self.video_slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.video_slider)

        # Thêm các nút điều khiển video
        video_controls = QHBoxLayout()
        self.play_button = ModernButton("Play", "#4CAF50")
        self.pause_button = ModernButton("Pause", "#f44336")
        self.play_button.clicked.connect(self.play_video)
        self.pause_button.clicked.connect(self.pause_video)
        video_controls.addWidget(self.play_button)
        video_controls.addWidget(self.pause_button)
        layout.addLayout(video_controls)

        display_frame.setLayout(layout)
        return display_frame

    def create_info_panel(self):
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout()

        # Tiêu đề
        title = QLabel("Detection Info")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        # Thêm danh sách video
        video_container = QWidget()
        video_layout = QVBoxLayout()
        video_title = QLabel("Video List")
        video_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        video_layout.addWidget(video_title)

        self.video_list = QListWidget()
        self.video_list.setStyleSheet("""
            QListWidget {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #3d3d3d;
            }
        """)
        self.video_list.itemClicked.connect(self.on_video_selected)
        video_layout.addWidget(self.video_list)
        video_container.setLayout(video_layout)

        # Phần hiển thị số lượng đối tượng (2/3 panel phía trên)
        self.stats_list = QListWidget()
        self.stats_list.setStyleSheet("""
            QListWidget {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #3d3d3d;
            }
        """)
        stats_container = QWidget()
        stats_layout = QVBoxLayout()
        stats_title = QLabel("Objects Count")
        stats_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        stats_layout.addWidget(stats_title)
        stats_layout.addWidget(self.stats_list)
        stats_container.setLayout(stats_layout)

        # Phần hiển thị log (1/3 panel phía dưới)
        log_container = QWidget()
        log_layout = QVBoxLayout()
        log_title = QLabel("Detection Log")
        log_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        log_layout.addWidget(log_title)
        self.info_list = QListWidget()
        self.info_list.setStyleSheet("""
            QListWidget {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #3d3d3d;
            }
        """)
        log_layout.addWidget(self.info_list)
        log_container.setLayout(log_layout)

        # Thêm video_container vào splitter
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(video_container)
        splitter.addWidget(stats_container)  # Stats container đã có từ trước
        splitter.addWidget(log_container)  # Log container đã có từ trước
        splitter.setStretchFactor(0, 1)  # Video list chiếm 1/4
        splitter.setStretchFactor(1, 2)  # Stats chiếm 2/4
        splitter.setStretchFactor(2, 1)  # Log chiếm 1/4

        layout.addWidget(splitter)
        panel.setLayout(layout)
        return panel

    def apply_styles(self):
        # Áp dụng dark theme
        self.setStyle(QStyleFactory.create("Fusion"))
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)

        self.setPalette(dark_palette)

        # Style chung cho ứng dụng
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #3d3d3d;
                border-radius: 4px;
            }
            QLabel {
                color: #ffffff;
            }
            QListWidget {
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
                background-color: #2d2d2d;
            }
            QComboBox {
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
                background-color: #2d2d2d;
            }
        """)

    def browse_input(self):
        input_type = self.input_combo.currentText()
        if input_type == "Video":
            file_names, _ = QFileDialog.getOpenFileNames(
                self,
                "Chọn Video",
                "",
                "Video Files (*.mp4 *.avi *.mkv)"
            )
            if file_names:
                # Lưu video đầu tiên làm nguồn input mặc định
                self.input_source = file_names[0]

                # Thêm tất cả video vào danh sách
                for file_name in file_names:
                    item = QListWidgetItem(file_name)
                    self.video_list.addItem(item)
                    self.info_list.addItem(f"Đã thêm video: {file_name}")

                # Tự động chọn video đầu tiên
                self.video_list.setCurrentRow(0)
                self.load_video(file_names[0])

    def start_detection(self):
        try:
            if hasattr(self, 'detection_thread') and self.detection_thread.isRunning():
                return

            selected_objects = [item.text().lower() for item in self.object_list.selectedItems()]
            if not selected_objects:
                self.info_list.addItem("Vui lòng chọn ít nhất một đối tượng để phát hiện!")
                return

            if not hasattr(self, 'input_source') and self.input_combo.currentText() != "Camera":
                self.info_list.addItem("Vui lòng chọn nguồn đầu vào!")
                return

            # Khởi tạo detector
            model = self.model_combo.currentText()
            if model not in YOLO_CONFIGS:
                self.info_list.addItem("Model không hợp lệ!")
                return

            config = YOLO_CONFIGS[model]
            try:
                self.detector = YOLODetector(
                    config['weights'],
                    config['config'],
                    config['conf_threshold'],
                    config['nms_threshold']
                )
            except Exception as e:
                self.info_list.addItem(f"Lỗi khởi tạo model: {str(e)}")
                return

            # Khởi tạo và start detection thread
            self.detection_thread = DetectionThread(
                self.detector,
                self.input_source if hasattr(self, 'input_source') else "Camera",
                selected_objects,
                self.object_colors,
                self.info_list
            )
            self.detection_thread.update_frame.connect(self.update_display)
            self.detection_thread.start()

            self.info_list.addItem("Bắt đầu phát hiện ��ối tượng...")
        except Exception as e:
            self.info_list.addItem(f"Lỗi khi bắt đầu phát hiện: {str(e)}")

    def stop_detection(self):
        if hasattr(self, 'detection_thread') and self.detection_thread.isRunning():
            self.detection_thread.running = False
            self.detection_thread.wait()
            self.info_list.addItem("Đã dừng phát hiện đối tượng")

    def update_display(self, frame, detections):
        if frame is None:
            return

        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        scaled_pixmap = pixmap.scaled(
            self.display_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.display_label.setPixmap(scaled_pixmap)

        # Cập nhật số lượng đối tượng
        self.update_object_stats(detections)

    def update_object_stats(self, detections):
        """Cập nhật số lượng đối tượng được phát hiện"""
        self.stats_list.clear()

        # Lấy danh sách các đối tượng được chọn
        selected_objects = [item.text().lower() for item in self.object_list.selectedItems()]

        # Đếm số lượng mỗi loại đối tượng từ detections
        object_counts = {}
        for detection in detections:
            class_name = detection[0]
            object_counts[class_name] = object_counts.get(class_name, 0) + 1

        # Hiển thị kết quả cho tất cả các đối tượng được chọn
        for obj_name in selected_objects:
            count = object_counts.get(obj_name, 0)  # Lấy số lượng, mặc định là 0
            item = QListWidgetItem(f"{obj_name}: {count}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)

            # Tạo màu khác nhau cho các đối tượng khác nhau
            color = self.get_object_color(obj_name)
            item.setForeground(QColor(color))

            self.stats_list.addItem(item)

    def get_object_color(self, object_name):
        """Trả về màu cố định cho mỗi loại đối tượng"""
        object_name = object_name.lower()
        return self.object_colors.get(object_name, {'hex': '#FFFFFF'})['hex']

    def on_video_selected(self, item):
        """Xử lý khi chọn video từ danh sách"""
        try:
            # Dừng thread hiện tại nếu đang chạy
            if hasattr(self, 'detection_thread') and self.detection_thread.isRunning():
                self.detection_thread.stop()
                self.detection_thread.wait()

            file_path = item.text()
            self.input_source = file_path
            self.load_video(file_path)

            # Tự động bắt đầu phát hiện
            self.start_detection()
        except Exception as e:
            self.info_list.addItem(f"Lỗi khi chọn video: {str(e)}")

    def load_video(self, file_path):
        """Tải video và cập nhật slider"""
        try:
            cap = cv2.VideoCapture(file_path)
            if not cap.isOpened():
                self.info_list.addItem("Không thể mở file video!")
                return

            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.video_slider.setRange(0, total_frames)
            self.video_slider.setValue(0)
            cap.release()
        except Exception as e:
            self.info_list.addItem(f"Lỗi khi tải video: {str(e)}")

    def on_slider_changed(self, value):
        """Xử lý khi kéo thanh slider"""
        if hasattr(self, 'detection_thread') and self.detection_thread.isRunning():
            self.detection_thread.set_frame_position(value)

    def play_video(self):
        """Phát video"""
        if hasattr(self, 'detection_thread') and not self.detection_thread.isRunning():
            self.start_detection()

    def pause_video(self):
        """Tạm dừng video"""
        if hasattr(self, 'detection_thread') and self.detection_thread.isRunning():
            self.detection_thread.pause()

    def auto_load_videos(self):
        """Tự động load tất cả video từ thư mục videos"""
        video_dir = "videos"  # Thư mục chứa video

        # Tạo thư mục nếu chưa tồn tại
        if not os.path.exists(video_dir):
            os.makedirs(video_dir)
            self.info_list.addItem("Đã tạo thư mục videos")
            return

        # Lấy danh sách các file video
        video_extensions = ['.mp4', '.avi', '.mkv', '.mov']
        video_files = []

        for file in os.listdir(video_dir):
            if any(file.lower().endswith(ext) for ext in video_extensions):
                full_path = os.path.join(video_dir, file)
                video_files.append(full_path)

        # Thêm vào video list
        for video_path in video_files:
            item = QListWidgetItem(video_path)
            self.video_list.addItem(item)

        if video_files:
            self.info_list.addItem(f"Đã tải {len(video_files)} video từ thư mục videos")
        else:
            self.info_list.addItem("Không tìm thấy video trong thư mục videos")

    def start_camera_detection(self):
        try:
            # Dừng detection thread hiện tại nếu đang chạy
            if hasattr(self, 'detection_thread') and self.detection_thread.isRunning():
                self.detection_thread.stop()
                self.detection_thread.wait()

            selected_objects = [item.text().lower() for item in self.object_list.selectedItems()]
            if not selected_objects:
                self.info_list.addItem("Vui lòng chọn ít nhất một đối tượng để phát hiện!")
                return

            # Khởi tạo detector
            model = self.model_combo.currentText()
            if model not in YOLO_CONFIGS:
                self.info_list.addItem("Model không hợp lệ!")
                return

            config = YOLO_CONFIGS[model]
            try:
                self.detector = YOLODetector(
                    config['weights'],
                    config['config'],
                    config['conf_threshold'],
                    config['nms_threshold']
                )
            except Exception as e:
                self.info_list.addItem(f"Lỗi khởi tạo model: {str(e)}")
                return

            # Khởi tạo detection thread với nguồn là camera
            self.detection_thread = DetectionThread(
                self.detector,
                "Camera",
                selected_objects,
                self.object_colors,
                self.info_list
            )
            self.detection_thread.update_frame.connect(self.update_display)
            self.detection_thread.start()

            self.info_list.addItem("Bắt đầu nhận diện qua camera...")
        except Exception as e:
            self.info_list.addItem(f"Lỗi khi khởi động camera: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

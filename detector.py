import torch
import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal
from utils import draw_detections


class YOLODetector:
    def __init__(self, weights_path, config_path, conf_threshold=0.5, nms_threshold=0.4):
        # Kiểm tra CUDA
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        if torch.cuda.is_available():
            print(f"Đang sử dụng GPU: {torch.cuda.get_device_name(0)}")
            print(f"CUDA version: {torch.version.cuda}")
        else:
            print("Không tìm thấy GPU, sử dụng CPU")

        # Tải model lên GPU nếu có
        self.net = cv2.dnn.readNet(weights_path, config_path)
        if self.device.type == 'cuda':
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

        self.conf_threshold = conf_threshold
        self.nms_threshold = nms_threshold

        with open("coco.names", "r") as f:
            self.classes = [line.strip() for line in f.readlines()]

        self.output_layers = [self.net.getLayerNames()[i - 1] for i in self.net.getUnconnectedOutLayers()]

    def detect(self, frame, target_objects):
        height, width, _ = frame.shape

        # Chuyển frame sang blob
        blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)

        # KHÔNG chuyển blob sang tensor PyTorch, giữ nguyên dạng numpy array
        self.net.setInput(blob)
        outputs = self.net.forward(self.output_layers)

        class_ids = []
        confidences = []
        boxes = []

        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > self.conf_threshold and self.classes[class_id] in target_objects:
                    center_x, center_y, w, h = (detection[0:4] * np.array([width, height, width, height])).astype('int')
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    boxes.append([x, y, int(w), int(h)])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indices = cv2.dnn.NMSBoxes(boxes, confidences, self.conf_threshold, self.nms_threshold)

        detections = []
        for i in indices:
            box = boxes[i]
            class_name = self.classes[class_ids[i]]
            conf = confidences[i]
            detections.append((class_name, conf, box))

        return detections


class DetectionThread(QThread):
    update_frame = pyqtSignal(np.ndarray, list)  # Thêm list để truyền detections

    def __init__(self, detector, input_source, target_objects, object_colors):
        super().__init__()
        self.detector = detector
        self.input_source = input_source
        self.target_objects = target_objects
        self.object_colors = object_colors
        self.running = True
        self.paused = False
        self.current_frame = 0
        self.frame_cache = {}  # Cache để lưu kết quả đã xử lý
        self.cache_size = 30  # Số frame tối đa được cache

    def set_frame_position(self, frame_number):
        """Đặt vị trí frame hiện tại"""
        self.current_frame = frame_number
        if hasattr(self, 'cap'):
            # Kiểm tra cache trước
            if frame_number in self.frame_cache:
                frame, detections = self.frame_cache[frame_number]
                self.update_frame.emit(frame, detections)
                return

            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = self.cap.read()
            if ret:
                detections = self.detector.detect(frame, self.target_objects)
                frame = draw_detections(frame, detections, self.object_colors)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Lưu vào cache
                self.frame_cache[frame_number] = (frame.copy(), detections)
                if len(self.frame_cache) > self.cache_size:
                    # Xóa frame cũ nhất nếu cache đầy
                    oldest_frame = min(self.frame_cache.keys())
                    del self.frame_cache[oldest_frame]

                self.update_frame.emit(frame, detections)

    def pause(self):
        """Tạm dừng/tiếp tục video"""
        self.paused = not self.paused

    def run(self):
        try:
            if self.input_source == "Camera":
                cap = cv2.VideoCapture(1)
            else:
                # Thêm các flag để xử lý video tốt hơn
                cap = cv2.VideoCapture(self.input_source, cv2.CAP_FFMPEG)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)

            if not cap.isOpened():
                print(f"Không thể mở nguồn video: {self.input_source}")
                return

            self.cap = cap

            # Lấy thông tin video
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_delay = int(1000 / fps) if fps > 0 else 30

            while self.running and cap.isOpened():
                if self.paused:
                    self.msleep(100)
                    continue

                ret, frame = cap.read()
                if not ret:
                    break

                try:
                    current_pos = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

                    if current_pos in self.frame_cache:
                        frame, detections = self.frame_cache[current_pos]
                    else:
                        detections = self.detector.detect(frame, self.target_objects)
                        frame = draw_detections(frame, detections, self.object_colors)
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                        self.frame_cache[current_pos] = (frame.copy(), detections)
                        if len(self.frame_cache) > self.cache_size:
                            oldest_frame = min(self.frame_cache.keys())
                            del self.frame_cache[oldest_frame]

                    self.update_frame.emit(frame, detections)
                    self.msleep(frame_delay)  # Đồng bộ với FPS của video

                except Exception as e:
                    print(f"Lỗi xử lý frame {current_pos}: {str(e)}")
                    continue

            cap.release()
        except Exception as e:
            print(f"Lỗi trong detection thread: {str(e)}")

    def stop(self):
        self.running = False

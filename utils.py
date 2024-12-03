import cv2
import numpy as np


def draw_detections(frame, detections, object_colors):
    """Vẽ các kết quả phát hiện với màu nền mờ"""
    overlay = frame.copy()

    for class_name, confidence, box in detections:
        x, y, w, h = box

        # Lấy màu từ dict màu đã được định nghĩa
        color = object_colors.get(class_name.lower(), {'rgb': (255, 255, 255)})['rgb']

        # Vẽ hình chữ nhật với màu nền mờ
        cv2.rectangle(overlay, (x, y), (x + w, y + h), color, -1)

        # Vẽ viền
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

        # Thêm nhãn
        label = f"{class_name}: {confidence:.2f}"
        (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(frame, (x, y - label_h - 10), (x + label_w, y), color, -1)
        cv2.putText(frame, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    # Kết hợp frame gốc với overlay
    alpha = 0.3  # Độ mờ (0-1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    return frame

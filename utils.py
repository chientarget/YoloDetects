import cv2
import numpy as np


def draw_detections(frame, detections, object_colors):
    """Vẽ các kết quả phát hiện với màu nền mờ"""
    overlay = frame.copy()

    for class_name, confidence, box in detections:
        x, y, w, h = box

        # Lấy màu từ dict màu đã được định nghĩa
        color = object_colors.get(class_name.lower(), {'rgb': (0, 0, 0)})['rgb']

        # Vẽ hình chữ nhật với màu nền mờ
        cv2.rectangle(overlay, (x, y), (x + w, y + h), color, -1)

        # Vẽ viền đậm hơn
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 3)  # Tăng độ dày viền lên 3

        # Thêm nhãn với font size lớn hơn
        label = f"{class_name}: {confidence:.2f}"
        font_scale = 1.5  # Tăng kích thước font
        font_thickness = 3  # Tăng độ dày font

        # Tính toán kích thước text để vẽ background
        (label_w, label_h), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)

        # Vẽ background cho text với padding
        padding = 5
        cv2.rectangle(frame,
                      (x, y - label_h - 2 * padding),
                      (x + label_w + 2 * padding, y),
                      color,
                      -1)

        # Vẽ text
        cv2.putText(frame,
                    label,
                    (x + padding, y - padding),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    font_scale,
                    (255, 255, 255),
                    font_thickness)

    # Kết hợp frame gốc với overlay
    alpha = 0.3  # Độ mờ (0-1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    return frame

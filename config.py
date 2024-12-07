YOLO_CONFIGS = {
    "YOLOv2": {
        "weights": "YOLO_MODEL/YOLO_V2/yolov2.weights",
        "config": "YOLO_MODEL/YOLO_V2/yolov2.cfg",
        "conf_threshold": 0.5,
        "nms_threshold": 0.4
    },
    "YOLOv3": {
        "weights": "YOLO_MODEL/YOLO_V3/yolov3.weights",
        "config": "YOLO_MODEL/YOLO_V3/yolov3.cfg",
        "conf_threshold": 0.5,
        "nms_threshold": 0.4
    },
    "YOLOv4": {
        "weights": "YOLO_MODEL/YOLO_V4/yolov4.weights",
        "config": "YOLO_MODEL/YOLO_V4/yolov4.cfg",
        "conf_threshold": 0.5,
        "nms_threshold": 0.4
    }
}

CLASSES = [
    # Con người và phương tiện giao thông (9)
    "person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
    
    # Biển báo và thiết bị giao thông (4)
    "traffic light", "fire hydrant", "stop sign", "parking meter",
    
    # Đồ nội thất và thiết bị gia dụng (6)
    "bench", "chair", "sofa", "bed", "diningtable", "toilet",
    
    # Động vật (10)
    "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe",
    
    # Đồ dùng cá nhân (5)
    "backpack", "umbrella", "handbag", "tie", "suitcase",
    
    # Dụng cụ thể thao (10)
    "frisbee", "skis", "snowboard", "sports ball", "kite", 
    "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket",
    
    # Đồ dùng nhà bếp và bàn ăn (7)
    "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl",
    
    # Thực phẩm (10)
    "banana", "apple", "sandwich", "orange", "broccoli", "carrot",
    "hot dog", "pizza", "donut", "cake",
    
    # Thiết bị điện tử và gia dụng (12)
    "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
    "microwave", "oven", "toaster", "sink", "refrigerator", "pottedplant",
    
    # Đồ dùng khác và vật dụng cá nhân (7)
    "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"
]
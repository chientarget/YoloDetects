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
    "person", "bicycle", "car", "motorcycle", "motorbike", "bus", "train", "truck",
    "traffic light", "stop sign", "parking meter",
    "tv", "laptop", "mouse", "keyboard", "cell phone"
]

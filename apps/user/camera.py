import cv2
import os
import urllib.request

import torch

from models.experimental import attempt_load
from utils.general import check_img_size, non_max_suppression, scale_coords, set_logging
from utils.plots import plot_one_box
from utils.torch_utils import select_device, time_synchronized
import numpy as np

######################### Helper Function for deep learning model ######################################
opt = {
    "weights": "./apps/api/views/best.pt",  # Path to weights file default weights are for nano model
    "yaml": "./apps/api/views/data.yaml",
    "img-size": 640,  # default image size
    "conf-thres": 0.25,  # confidence threshold for inference.
    "iou-thres": 0.45,  # NMS IoU threshold for inference.
    "device": 'cpu',  # device to run our model i.e. 0 or 0,1,2,3 or cpu
    "classes": ['None']  # list of classes to filter or None
}


def letterbox(img, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleFill=False, scaleup=True, stride=32):
    # Resize and pad image while meeting stride-multiple constraints
    shape = img.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)

    # Scale ratio (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    if not scaleup:  # only scale down, do not scale up (for better test mAP)
        r = min(r, 1.0)

    # Compute padding
    ratio = r, r  # width, height ratios
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
    if auto:  # minimum rectangle
        dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding
    elif scaleFill:  # stretch
        dw, dh = 0.0, 0.0
        new_unpad = (new_shape[1], new_shape[0])
        ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]  # width, height ratios

    dw /= 2  # divide padding into 2 sides
    dh /= 2

    if shape[::-1] != new_unpad:  # resize
        img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
    return img, ratio, (dw, dh)


def count(founded_classes, im0):
    model_values = []
    aligns = im0.shape
    align_bottom = aligns[0]
    align_right = (aligns[1] / 2)
    number = 0
    for i, (k, v) in enumerate(founded_classes.items()):
        a = f"{k}={v}"
        model_values.append(v)
        align_bottom = align_bottom - 35
        cv2.putText(im0, str(a), (int(align_right), align_bottom), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1,
                    cv2.LINE_AA)
        number = v
    return number


###############################################################


class Webcam(object):
    def __init__(self):

        # Load Model
        self.weights, self.imgsz = opt['weights'], opt['img-size']
        set_logging()
        self.device = select_device(opt['device'])
        self.half = self.device.type != 'cpu'
        self.model = attempt_load(self.weights, map_location=self.device)  # load FP32 model
        self.stride = int(self.model.stride.max())  # model stride
        self.imgsz = check_img_size(self.imgsz, s=self.stride)  # check img_size
        if self.half:
            self.model.half()

        self.names = self.model.module.names if hasattr(self.model, 'module') else self.model.names

        if self.device.type != 'cpu':
            self.model(torch.zeros(1, 3, self.imgsz, self.imgsz).to(self.device).type_as(next(self.model.parameters())))
        print("Initttt")
        self.video_c = cv2.VideoCapture(0)

    def __del__(self):
        self.video_c.release()

    def get_frame(self):

        # Get Video information
        fps = self.video_c.get(cv2.CAP_PROP_FPS)
        w = int(self.video_c.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self.video_c.get(cv2.CAP_PROP_FRAME_HEIGHT))
        nframes = int(self.video_c.get(cv2.CAP_PROP_FRAME_COUNT))

        while self.video_c.isOpened():
            print("Processing")

            # Read Image In
            ret, img0 = self.video_c.read()
            img0 = cv2.flip(img0, 1)
            img = letterbox(img0, self.imgsz, stride=self.stride)[0]
            img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
            img = np.ascontiguousarray(img)
            img = torch.from_numpy(img).to(self.device)
            img = img.half() if self.half else img.float()  # uint8 to fp16/32
            img /= 255.0  # 0 - 255 to 0.0 - 1.0
            if img.ndimension() == 3:
                img = img.unsqueeze(0)
            # Inference
            t1 = time_synchronized()
            pred = self.model(img, augment=False)[0]

            # Apply NMS
            classes = None
            if opt['classes']:
                classes = []
                for class_name in opt['classes']:
                    classes.append(opt['classes'].index(class_name))

            pred = non_max_suppression(pred, opt['conf-thres'], opt['iou-thres'], classes=classes,
                                       agnostic=False)
            t2 = time_synchronized()

            for i, det in enumerate(pred):
                s = ''
                s += '%gx%g ' % img.shape[2:]  # print string
                if len(det):
                    det[:, :4] = scale_coords(img.shape[2:], det[:, :4], img0.shape).round()
                    founded_classes = {}  # Creating a dict to storage our detected items
                    # Print results
                    for c in det[:, -1].unique():
                        n = (det[:, -1] == c).sum()  # detections per class
                        class_index = int(c)

                        founded_classes[self.names[class_index]] = int(n)
                        s += f"{n} {self.names[int(c)]}{'s' * (n > 1)}, "  # add to string
                        count(founded_classes=founded_classes, im0=img0)  # Applying counter function

                    for *xyxy, conf, cls in reversed(det):
                        label = f'{self.names[int(cls)]} {conf:.2f}'
                        plot_one_box(xyxy, img0, label=label, color=1,
                                     line_thickness=1)  # color=colors[int(c

            ret, jpeg = cv2.imencode('.jpeg', img0)
            return jpeg.tobytes()

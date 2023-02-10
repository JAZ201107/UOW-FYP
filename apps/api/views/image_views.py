import os.path

from rest_framework import views
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from apps.api import models
from apps.api import serializers
import numpy as np
import base64
from torchvision import transforms
import io
import PIL

import boto3
import urllib.request
from django.conf import settings

################################ Packages and Methods for Deep Learning Model ################################
########################### Packages for Deep Learning Model ############################
import cv2
import torch

from models.experimental import attempt_load
from utils.general import check_img_size, non_max_suppression, scale_coords, set_logging
from utils.plots import plot_one_box
from utils.torch_utils import select_device, time_synchronized

############################################################################################################

########################### Methods for Deep Learning Model ############################
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


def detect_image(image_url, **kwargs):
    """This function get the url of the source image and other information about user
    Counting the Maizes, and store the Image back to AWS S3 and related information into database"""
    number = 0  # the number of Maize
    # Process the Images
    with torch.no_grad():
        weights, imgsz = opt['weights'], opt['img-size']
        set_logging()
        device = select_device(opt['device'])
        half = device.type != 'cpu'
        model = attempt_load(weights, map_location=device)  # load FP32 model
        stride = int(model.stride.max())  # model stride
        imgsz = check_img_size(imgsz, s=stride)  # check img_size
        if half:
            model.half()

        names = model.module.names if hasattr(model, 'module') else model.names

        if device.type != 'cpu':
            model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))

        req = urllib.request.urlopen(image_url)
        arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
        img0 = cv2.imdecode(arr, -1)  # 'Load it as it is'
        # img0 = cv2.imread(source_image_path)
        img = letterbox(img0, imgsz, stride=stride)[0]
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        img = np.ascontiguousarray(img)
        img = torch.from_numpy(img).to(device)
        img = img.half() if half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        # Inference
        t1 = time_synchronized()
        pred = model(img, augment=False)[0]

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

                    founded_classes[names[class_index]] = int(n)
                    s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string
                    number = count(founded_classes=founded_classes, im0=img0)  # Applying counter function

                for *xyxy, conf, cls in reversed(det):
                    label = f'{names[int(cls)]} {conf:.2f}'
                    plot_one_box(xyxy, img0, label=label, color=1,
                                 line_thickness=1)  # color=colors[int(c
        img_string = cv2.imencode('.jpg', img0)[1].tobytes()

        session = boto3.Session(
            aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY
        )
        s3 = session.client("s3")
        s3.put_object(Body=img_string, Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=kwargs['image_detected_url'])
        store_detect_images(
            user_email=kwargs['user_email'],
            origin_image_url=image_url,
            detect_image_url=kwargs['image_detected_url'],
            counted_number=number
        )
        # Detect the image success
    return number


def store_detect_images(**kwargs):
    user_email = kwargs['user_email']
    origin_image_url = kwargs['origin_image_url']
    detect_image_url = kwargs['detect_image_url']
    detect_image_url = "/".join(["https://learn-aws-1211.s3.ap-southeast-1.amazonaws.com", detect_image_url])
    counted_number = kwargs['counted_number']
    print(kwargs)
    models.UserDetectedImageModel.objects.create(
        user_email=user_email,
        origin_image_url=origin_image_url,
        detect_image_url=detect_image_url,
        counted_number=counted_number
    )


############################################################################################################


class ReceiveImageModelView(views.APIView):
    """This class handle the uploaded image"""
    serializer_class = serializers.ReceiveImageModelSerializer
    queryset = models.ReceiveImageModel.objects.all()

    def get(self, request):
        pass

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            content = {}  # the return content
            user_email = serializer.validated_data.get('user_email')
            image = serializer.validated_data.get('image')
            # serializer.save()
            if serializer.save():  # save the user email and un-counted image
                # If model is successfully saved
                image_url = "/".join([settings.BASE_URI, user_email, image.name])  # the URL of the uploaded image
                # the path that the detected image will be stored
                image_detected_url = "/".join(["images", user_email, "detect", image.name])
                # the path that will return to the front end
                image_detected_url_return = "/".join([settings.BASE_URI, user_email, "detect", image.name])
                content['image_detected_url_return'] = image_detected_url_return
                content['image_url'] = image_url

                number = detect_image(image_url, image_detected_url=image_detected_url, user_email=user_email)
                content['counted'] = number
                return Response(content, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

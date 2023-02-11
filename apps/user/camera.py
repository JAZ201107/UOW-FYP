import cv2
import os
import urllib.request


class Webcam(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        # encode raw image into JPEG formaat
        image = cv2.flip(image, 1)
        ret, jpeg = cv2.imencode('.jpeg', image)
        return jpeg.tobytes()

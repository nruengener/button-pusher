import time
import picamera
import numpy as np
import cv2

from button_detection.button_detector import ButtonDetector

detector = ButtonDetector()

with picamera.PiCamera() as camera:
    camera.resolution = (320, 240)
    camera.framerate = 24
    time.sleep(2)
    image = np.empty((240, 320, 3), dtype=np.uint8)
    camera.capture(image, 'bgr')

    start = time.time()
    image_detected, boxes = detector.detect_buttons(image.copy())
    end = time.time()
    print("[INFO] Conversion and button detection took {:.5} seconds".format(end - start))
    cv2.imshow('detected buttons', image_detected)

import time
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import cv2

print("Hello RaspberryPi")

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.hflip = True
camera.vflip = True

rawCapture = PiRGBArray(camera)

# allow the camera to warmup
time.sleep(2)

# grab an image from the camera
camera.capture(rawCapture, format="bgr")
image = rawCapture.array

# display the image on screen and wait for a keypress
cv2.imshow("Image", image)
cv2.waitKey(0)

# with picamera.PiCamera() as camera:
#     camera.start_preview()
#     time.sleep(10)
#     camera.stop_preview()



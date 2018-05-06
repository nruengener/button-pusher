import math
import platform
import time
import cv2
import numpy as np
import serial_com
from button_detection.button_detector import ButtonDetector
from button_detection.image_processing import resize_to_width, convert_boxes
from object_tracker import FeatureTracker
from pi_video_stream import PiVideoStream
from movement import Movement

print("OpenCV version: ", cv2.__version__)
print(platform.python_version())

DEBUG = True

serial_communication = serial_com.SerialCom('/dev/ttyACM0', 9600)

vs = PiVideoStream()

# use keypoint matcher (provided trackers like KFC, MIL etc. do not work properly cause of vibration)
# tracker = ThreadedObjectTracker(vs)
tracker = FeatureTracker(vs)

movement = Movement(serial_communication, tracker)

detector = ButtonDetector()


def init():
    # serial communication with Arduino
    serial_communication.init_communication()
    serial_communication.read_all()  # clear on start

    # vs.start()
    time.sleep(1.0)


# shutdown all handles
def shutdown():
    tracker.stop()
    serial_communication.close()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    try:
        init()

        # wait for user input
        # todo: handle user input

        # enable motors before cam to get a stable first image
        # print(serial_communication.write("M17"))
        # move to allow sideway movement to determine distance
        movement.move_cartesian(0, 20, 15)
        time.sleep(.4)

        # image = vs.read()
        image = tracker.get_current_frame()
        img_resized = resize_to_width(image.copy(), 400, True)

        # detect buttons in image
        # todo: resize image
        start = time.time()
        image_detected, boxes = detector.detect_buttons(img_resized)
        end = time.time()
        print("[INFO] Conversion and button detection took {:.5} seconds".format(end - start))
        if DEBUG:
            cv2.imshow('detected buttons', image_detected)

        if len(boxes) <= 0:
            print("No buttons detected")
            exit(0)  # todo: just break loop and wait for input

        # resize boxes
        boxes = convert_boxes(boxes, image)

        # find box with desired text
        # todo: implement (using tesseract)

        # todo: remove
        bbox = boxes[0]

        # define bounding box (this will be replaced with box from deep learning method)
        # bbox = cv2.selectROI(image, False)
        print("selected bbox: ", bbox)

        ok = movement.move_to_target(image, bbox)
        if not ok:
            print("Could not move to target")

        # todo: warn if out of reach?

        movement.move_home()

        #  disable motors
        serial_communication.write("M18")

        # cv2.imshow("After", image)
        cv2.waitKey(0)

    finally:
        #  disable motors
        serial_communication.write("M18")
        shutdown()
        print("exiting...")


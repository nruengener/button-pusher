import math
import platform
import time

import cv2

from interfaces import serial_com
from config import *
from image_processing.object_tracker import FeatureTracker
from image_processing.pi_video_stream import PiVideoStream
from movement import Movement

print("OpenCV version: ", cv2.__version__)
print(platform.python_version())

focal_pixel = (CAMERA_WIDTH * 0.5) / math.tan(HFOV * 0.5 * math.pi/180)

serial_communication = serial_com.SerialCom('/dev/ttyACM0', 9600)
# camera = PiCamera(resolution=(CAMERA_WIDTH, CAMERA_HEIGHT), framerate=10)
vs = PiVideoStream()

# use keypoint matcher (provided trackers like KFC, MIL etc. do not work properly cause of vibration)
# tracker = ThreadedObjectTracker(vs)
tracker = FeatureTracker(vs)

movement = Movement(serial_communication, tracker)


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

        # enable motors before cam to get a stable first image
        print(serial_communication.write("M17"))
        # move to allow sideway movement to determine distance
        movement.move_cartesian(0, 20, 15)
        time.sleep(.4)

        # image = vs.read()
        image = tracker.get_current_frame()

        # define bounding box (this will be replaced with box from deep learning method)
        bbox = cv2.selectROI(image, False)
        print("selected bbox: ", bbox)

        # result = movement.center_on_target(image, bbox)
        # ok = movement.get_distance_by_moving(image, bbox)
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


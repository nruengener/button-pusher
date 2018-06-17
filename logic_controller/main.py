import platform
import time
import traceback

import cv2
from RPi import GPIO

from button_detection.button_detector import ButtonDetector
from button_detection.image_processing import resize_to_width, convert_boxes
from image_processing.object_tracker import FeatureTracker
from image_processing.pi_video_stream import PiVideoStream
from interfaces import serial_com
from interfaces.keypad import KeyPad
from movement import Movement
from text_recognition.text_processing import find_target

GPIO.setwarnings(False)

print("OpenCV version: ", cv2.__version__)
print(platform.python_version())

DEBUG = True

serial_communication = serial_com.SerialCom('/dev/ttyACM0', 9600)

vs = PiVideoStream()

# use keypoint matcher (provided trackers like KCF, MIL etc. do not work properly cause of vibration)
# tracker = ThreadedObjectTracker(vs)
tracker = FeatureTracker(vs)

movement = Movement(serial_communication, tracker)

# object detector for elevator buttons
detector = ButtonDetector()

keypad = KeyPad()


def init():
    # serial communication with Arduino
    serial_communication.init_communication()
    serial_communication.read_all()  # clear on start
    im = tracker.get_current_frame()
    imr = resize_to_width(im.copy(), 800, True)
    id, b = detector.detect_buttons(imr)


# shutdown all handles
def shutdown():
    tracker.stop()
    serial_communication.close()
    cv2.destroyAllWindows()
    keypad.shutdown()


if __name__ == '__main__':
    try:
        init()
    except Exception as err:
        print("Error initializing the system: ", err)

    while True:
        try:
            # test reproduction / movement
            # print(serial_communication.write("M17"))
            # time.sleep(.2)
            # for x in range(0, 3):
            #     movement.move_cartesian(0, 20, 15)
            #     time.sleep(2)
            #     movement.move_cartesian(0, 150, 0)
            #     time.sleep(2)
            #     movement.move_home()
            #     time.sleep(.5)
            #
            # serial_communication.write("M18")
            # exit(0)

            # todo: led for ready state
            # wait for user input
            # keypad.start_input()
            # print("waiting for user input")
            # while not keypad.input_finished():
            #     time.sleep(0.1)
            #
            # input_string = keypad.get_input()
            # input_number = int(input_string)
            # print("number entered: ", input_number)
            input_string = "0"

            # enable motors before cam to get a stable first image
            print(serial_communication.write("M17"))
            # move to allow sideway movement to determine distance
            movement.move_cartesian(0, 20, 15)
            time.sleep(.4)

            # image = vs.read()
            image = tracker.get_current_frame()
            img_resized = resize_to_width(image.copy(), 800, True)

            if DEBUG:
                cv2.imshow('start image', img_resized)

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
                movement.move_home()
                serial_communication.write("M18")
                continue

            # resize boxes
            boxes = convert_boxes(boxes, image)
            # boxes = convert_boxes(boxes, img_resized)

            # find box with desired text
            start = time.time()
            target = find_target(boxes, image, input_string)  # todo: use confidence if more than one?
            # target = find_target(boxes, img_resized, input_string)
            end = time.time()
            print("[INFO] OCR took {:.5} seconds".format(end - start))

            # if target is None:
            #     boxes_ocr = recognize_text_in_boxes(boxes, image)
            #     for (box, text) in boxes_ocr:
            #         if text == input_string:
            #             target = box
            #             break

            if target is None:
                print("Could not find button with ", input_string, " as label")
                # # todo: break outer loop instead of exit
                # cv2.waitKey(0)
                # exit(0)
                movement.move_home()
                serial_communication.write("M18")
                continue

            print("selected bbox: ", target)
            ok = movement.move_to_target(image, target)
            if not ok:
                print("Could not move to target")

            # move to home position
            movement.move_home()

            #  disable motors
            serial_communication.write("M18")

            if DEBUG:
                cv2.waitKey(0)

        except Exception as err:
            print("Error during system run: ", err)
            traceback.print_tb(err.__traceback__)

        finally:
            serial_communication.write("M18")  # disable motors in case of exception due to overheating

    #  disable motors
    serial_communication.write("M18")
    shutdown()
    print("exiting...")


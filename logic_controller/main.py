import PIL
import math
import platform
import time
import cv2
import imutils
import numpy as np
import pytesseract
from RPi import GPIO
from pytesseract import Output

from button_detection import image_processing
from config import TRACE
from interfaces import serial_com
from button_detection.button_detector import ButtonDetector
from button_detection.image_processing import resize_to_width, convert_boxes
from image_processing.object_tracker import FeatureTracker
from image_processing.pi_video_stream import PiVideoStream
from interfaces.keypad import KeyPad
from movement import Movement
from tesserocr import PyTessBaseAPI, PSM

print("OpenCV version: ", cv2.__version__)
print(platform.python_version())

DEBUG = True

serial_communication = serial_com.SerialCom('/dev/ttyACM0', 9600)

vs = PiVideoStream()

# use keypoint matcher (provided trackers like KFC, MIL etc. do not work properly cause of vibration)
# tracker = ThreadedObjectTracker(vs)
tracker = FeatureTracker(vs)

movement = Movement(serial_communication, tracker)

# object detector for elevator buttons
detector = ButtonDetector()

keypad = KeyPad()


def init():
    GPIO.setwarnings(False)

    # serial communication with Arduino
    serial_communication.init_communication()
    serial_communication.read_all()  # clear on start

    # vs.start()
    # time.sleep(0.2)


# shutdown all handles
def shutdown():
    tracker.stop()
    serial_communication.close()
    cv2.destroyAllWindows()
    keypad.shutdown()


if __name__ == '__main__':
    try:
        init()

        # wait for user input
        # todo: handle user input
        # keypad.start_input()
        # print("waiting for user input")
        # while not keypad.input_finished():
        #     time.sleep(0.1)
        #
        # input_string = keypad.get_input()
        # input_number = int(input_string)
        # print("number entered: ", input_number)
        input_string = "6"

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
            exit(0)  # todo: just break loop and wait for input

        # resize boxes
        boxes = convert_boxes(boxes, image)

        # find box with desired text
        # todo: implement (using tesseract)

        boxes_ocr = []
        for box in boxes:
            roi = image[box[1]:box[1] + box[3], box[0]:box[0] + box[2]]
            # rotated = imutils.rotate_bound(roi, - image_processing.detect_skew(roi))
            # preprocess region of interest
            img_preprocessed = image_processing.process_image(roi)

            ocr_result = pytesseract.image_to_string(img_preprocessed, lang='eng',
                                                     config='--oem 0 --psm 7 -c tessedit_char_whitelist=0123456789Ee')
            print("tesseract on whole region: ", ocr_result.strip())

            print("boxout whole region: ", pytesseract.image_to_boxes(img_preprocessed, lang='eng',
                                                         config="--oem 0 --psm 8 -c tessedit_char_whitelist=01234567890Ee"))

            # find tokens for OCR
            tokens = image_processing.find_tokens(img_preprocessed)
            text = ""
            i = 0
            for (x1, y1, x2, y2) in tokens:
                tesseract_img = roi[y1:y2, x1:x2]
                tesseract_img = image_processing.resize_to_width(tesseract_img, 300, False)
                tesseract_img = cv2.cvtColor(tesseract_img, cv2.COLOR_BGR2GRAY)
                ret, tesseract_img = cv2.threshold(tesseract_img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
                if TRACE:
                    cv2.imshow('tesser img' + str(i), tesseract_img)
                    i = i + 1
                # -psm 10 for single characters, -psm 8 (6?) for words
                # ocr_result = pytesseract.image_to_string(imgOCR, lang='eng', boxes=False,
                #                                          config='-psm 10 -c tessedit_char_whitelist=01234567890Ee')
                # print("tesseract ocr image: ", ocr_result.strip())

                # print("boxout: ", pytesseract.image_to_boxes(tesseract_img, lang='eng', config="--psm 10 -c tessedit_char_whitelist=01234567890Ee"))

                data = pytesseract.image_to_data(tesseract_img,  config="--psm 10 --oem 0 -c tessedit_char_whitelist=01234567890Ee",
                                                 output_type=Output.DICT)   # DICT

                ocr_result = pytesseract.image_to_string(tesseract_img, lang='eng',
                                                         config="--psm 10 --oem 0 -c tessedit_char_whitelist=01234567890Ee")  # -psm 10
                print("ocr result: ", ocr_result)

                # pil_img = PIL.Image.fromarray(tesseract_img)
                # with PyTessBaseAPI(psm=PSM.SINGLE_CHAR) as api:
                #     api.SetImage(pil_img)
                #     print("utf-8 text: ", api.GetUTF8Text())
                #     print("confidences: ", api.AllWordConfidences())

                # print("data: ", data)
                token_text = data['text']
                if data['conf'][len(data['conf'])-1] > 0:
                    text = text + data['text'][len(data['conf'])-1]
                print("token_text: ", token_text)
                print("data['conf']: ", data['conf'])

            print("text read from box: ", text)
            boxes_ocr.append((box, text))

        target = None
        for (box, text) in boxes_ocr:
            if text == input_string:
                target = box
                break

        if target is None:
            print("Could not find button with ", input_string, " as label")
            # todo: break outer loop
        # bbox = boxes[0]

        # define bounding box (this will be replaced with box from deep learning method)
        # bbox = cv2.selectROI(image, False)
        print("selected bbox: ", box)

        ok = movement.move_to_target(image, box)
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


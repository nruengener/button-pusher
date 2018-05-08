import cv2

from pytesseract import pytesseract, Output

from button_detection import image_processing
from config import TRACE
from text_recognition.token_util import filter_tokens


def find_target(boxes, image, label):
    """ Detect the box with the given label """
    for box in boxes:
        roi = image[box[1]:box[1] + box[3], box[0]:box[0] + box[2]]

        # preprocess region of interest
        img_preprocessed = image_processing.process_image(roi)

        # find tokens for OCR
        tokens = image_processing.find_tokens(img_preprocessed)
        tokens = filter_tokens(tokens, img_preprocessed)
        text = ""
        for (x1, y1, x2, y2) in tokens:
            tesseract_img = roi[y1:y2, x1:x2]
            tesseract_img = image_processing.resize_to_width(tesseract_img, 300, False)
            tesseract_img = cv2.cvtColor(tesseract_img, cv2.COLOR_BGR2GRAY)
            ret, tesseract_img = cv2.threshold(tesseract_img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

            data = pytesseract.image_to_data(tesseract_img,
                                             config="--psm 10 --oem 0 -c tessedit_char_whitelist=01234567890Ee",
                                             output_type=Output.DICT)  # DICT

            token_text = data['text']
            if data['conf'][len(data['conf']) - 1] > 0:
                text = text + data['text'][len(data['conf']) - 1]

        if label == text:
            return box

    return None


def recognize_text_in_boxes(boxes, image):
    boxes_ocr = []
    for box in boxes:
        roi = image[box[1]:box[1] + box[3], box[0]:box[0] + box[2]]

        # preprocess region of interest
        img_preprocessed = image_processing.process_image(roi)

        # find tokens for OCR
        tokens = image_processing.find_tokens(img_preprocessed)
        tokens = filter_tokens(tokens, img_preprocessed)
        print("# tokens for box ", box, ": ", len(tokens))
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

            data = pytesseract.image_to_data(tesseract_img,
                                             config="--psm 10 --oem 0 -c tessedit_char_whitelist=01234567890Ee",
                                             output_type=Output.DICT)  # DICT

            # ocr_result = pytesseract.image_to_string(tesseract_img, lang='eng',
            #                         config="--psm 10 --oem 0 -c tessedit_char_whitelist=01234567890Ee")  # -psm 10
            # print("ocr result: ", ocr_result)

            token_text = data['text']
            if data['conf'][len(data['conf']) - 1] > 0:
                text = text + data['text'][len(data['conf']) - 1]

            if TRACE:
                print("token_text: ", token_text)
                print("data['conf']: ", data['conf'])

        print("text read from box: ", text)
        boxes_ocr.append((box, text))

    return boxes_ocr



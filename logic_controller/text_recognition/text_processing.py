import cv2

from pytesseract import pytesseract, Output

from button_detection import image_processing
from config import TRACE, DEBUG
from text_recognition.token_util import filter_tokens

j = 0


def find_target(boxes, image, label):
    """ Detect the box with the given label """
    for box in boxes:
        roi = image[box[1]:box[1] + box[3], box[0]:box[0] + box[2]]

        # preprocess region of interest
        img_preprocessed = image_processing.process_image(roi)

        # find tokens for OCR, tokens are in format x1, y1, x2 ,y2
        tokens = image_processing.find_tokens(img_preprocessed)
        if TRACE:
            print("#tokens: ", len(tokens))
        tokens = filter_tokens(tokens, img_preprocessed)
        if TRACE:
            print("#filtered: ", len(tokens))

        if TRACE:
            for t in tokens:
                cv2.rectangle(img_preprocessed, (t[0], t[1]), (t[2], t[3]), (255, 200, 50), 2)
                global j
                cv2.imshow('filtered token ' + str(j), img_preprocessed)
                j = j + 1

        text = ""
        for (x1, y1, x2, y2) in tokens:
            tesseract_img = roi[y1:y2, x1:x2]
            tesseract_img = image_processing.resize_to_width(tesseract_img, 300, False)
            tesseract_img = cv2.cvtColor(tesseract_img, cv2.COLOR_BGR2GRAY)
            ret, tesseract_img = cv2.threshold(tesseract_img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

            data = pytesseract.image_to_data(tesseract_img,
                                             config="--psm 10 --oem 0 -c tessedit_char_whitelist=01234567890E",
                                             output_type=Output.DICT)  # DICT

            if TRACE:
                print("data['conf']: ", data['conf'])

            if data['conf'][len(data['conf']) - 1] > 60:
                text = text + data['text'][len(data['conf']) - 1]

        if DEBUG:
            print("button label: ", text)

        # return first box with searched label
        if label == text or (label == '0' and text == 'E') :
            return box

    return None


# not used anymore
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



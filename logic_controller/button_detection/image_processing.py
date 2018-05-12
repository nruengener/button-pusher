import cv2
import imutils
import numpy as np
import math
from config import *
# from tesserocr import PyTessBaseAPI


def detect_skew(image_np):
    """Detect skew in the image"""
    # find edges with canny
    edges = cv2.Canny(image_np, 100, 200)
    # find lines
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 75, None, 0, 0)

    # filter lines by theta and compute average
    theta_min = 60.0 * np.pi / 180
    theta_max = 120.0 * np.pi / 180
    theta_avr = 0.0
    theta_deg = 0.0

    # Copy edges to the images that will display the results in BGR
    cdst = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    cdstP = np.copy(cdst)
    # todo: test HoughLinesP ?

    filtered_lines = []
    if lines is not None:
        for i in range(0, len(lines)):
            rho = lines[i][0][0]
            theta = lines[i][0][1]
            if theta_min < theta < theta_max:
                filtered_lines.append(lines[i])
                theta_avr += theta
            # draw lines
            a = math.cos(theta)
            b = math.sin(theta)
            x0 = a * rho
            y0 = b * rho
            pt1 = (int(x0 + 1000 * (-b)), int(y0 + 1000 * a))
            pt2 = (int(x0 - 1000 * (-b)), int(y0 - 1000 * a))
            if TRACE:
                cv2.line(cdst, pt1, pt2, (0, 255, 0), 2)

    if len(filtered_lines) > 0:
        theta_avr /= len(filtered_lines)
        theta_deg = (theta_avr / (np.pi / 180)) - 90

    if TRACE:
        cv2.imshow("Skew Lines", cdst)

    return theta_deg


def filter_contours(contours):
    filtered_contours = []
    bounding_boxes = []
    # filter contours by bounding rect size
    for i in range(0, len(contours)):
        x, y, w, h = cv2.boundingRect(contours[i])
        if 20 < h < 500 and 5 < w < h:
            bounding_boxes.append((x, y, w, h))
            filtered_contours.append(contours[i])

    return bounding_boxes, filtered_contours


def find_aligned_boxes(bounding_boxes):
    """ Find boxes aligned at y position. """
    aligned_boxes = []
    if bounding_boxes is not None:
        first_box = bounding_boxes[0]
        for i in range(1, len(bounding_boxes)):
            if abs(bounding_boxes[i].y - first_box.y) < 10 and abs(first_box.height - bounding_boxes[i].height) < 5:
                aligned_boxes.append(bounding_boxes[i])

    return aligned_boxes


def find_tokens(image_np):
    """Find and isolate the tokens. Returns an array with boxes for all tokens in the roi.
    Tokens are in format x1, y1, x2 ,y2. """
    tokens = []

    # # find edges with canny
    # edges = cv2.Canny(image_np, 100, 200)  # 100, 200  todo: use canny only once
    img_copy = image_np.copy()

    # find contours in whole image
    # todo: use image with edges here instead of image_np?
    im2, contours, hierarchy = cv2.findContours(img_copy, cv2.RETR_TREE,
                                                cv2.CHAIN_APPROX_SIMPLE)  # CV_RETR_EXTERNAL, CV_CHAIN_APPROX_NONE
    # im2, contours, hierarchy = cv2.findContours(edges, cv2.RETR_LIST,
    #                                             cv2.CHAIN_APPROX_NONE)  # CV_RETR_EXTERNAL, CV_CHAIN_APPROX_NONE

    if TRACE:
        cv2.imshow('contours', im2)

    # filter contours by bounding rect size
    bounding_boxes, filtered_contours = filter_contours(contours)
    if TRACE:
        print("number of filtered contours: ", len(filtered_contours), " , boxes: ", len(bounding_boxes))

    # cut out found rectangles from edged image
    for i in range(0, len(bounding_boxes)):
        x, y, w, h = bounding_boxes[i]
        # apply padding for tesseract (important to improve text detection rate)
        if x > 5:
            x = x - 5
        if y > 5:
            y = y - 5
        w = w + 10
        h = h + 10
        tokens.append((x, y, x + w, y + h))
        if TRACE:
            cv2.rectangle(img_copy, (x, y), (x + w, y + h), (255, 200, 50), 2)
            cv2.imshow('token ' + str(i), img_copy)

    return tokens


def resize_to_width(image_np, width, only_shrink):
    """ Resize an image to the given width keeping the scale """
    h, w, d = image_np.shape
    # print("h: ", h, ", w: ", w, ", d: ", d)
    if only_shrink and w < width:
            return image_np

    imgScale = float(width) / w
    # print("imgScale: ", imgScale)
    newX, newY = image_np.shape[1] * imgScale, image_np.shape[0] * imgScale
    return cv2.resize(image_np, (int(newX), int(newY)))


def process_image(image_np):
    """ Preprocess image for finding tokens for OCR """
    # get grayscale image
    img_gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)

    # blur
    img_blurred = cv2.GaussianBlur(img_gray, (5, 5), 0)

    if TRACE:
        cv2.imshow('Unrotated/Blurred', img_blurred)

    # threshold image
    # ret, img_thresh = cv2.threshold(img_blurred, 60, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C)
    ret, img_thresh = cv2.threshold(img_blurred, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    # img_thresh = cv2.adaptiveThreshold(img_blurred,  # input image
    #                                    255,  # make pixels that pass the threshold full white
    #                                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    #                                    # cv2.CALIB_CB_ADAPTIVE_THRESH,
    #                                    # ADAPTIVE_THRESH_MEAN_C
    #                                    # use gaussian rather than mean, seems to give better results
    #                                    cv2.THRESH_BINARY,
    #                                    #  cv2.THRESH_BINARY_INV,
    #                                    # invert so foreground will be white, background will be black
    #                                    15,  # 11 # size of a pixel neighborhood used to calculate threshold value
    #                                    2)  # constant subtracted from the mean or weighted mean

    # dilate
    # kernel = np.ones((3, 3), np.uint8)  # 5 5
    # img_thresh = cv2.dilate(img_thresh, kernel, iterations=1)

    if TRACE:
        cv2.imshow('Threshold Dilated', img_thresh)

    # detect and correct skew
    if TRACE:
        print("skew: ", detect_skew(img_thresh))
    rotated = imutils.rotate_bound(img_thresh, - detect_skew(img_gray))  # fix skew

    return rotated


def convert_boxes(boxes, image_np):
    """ convert normalized bounding boxes to format of given image. Scale of origin image has to be the same. """
    height, width, depth = image_np.shape
    converted_boxes = []
    for (ymin, xmin, ymax, xmax) in boxes:
        # text recognition
        # print('xmin alt: ', xmin, 'xmin neu: ', int(xmin * width))
        xmin = int(xmin * width)
        ymin = int(ymin * height)
        xmax = int(xmax * width)
        ymax = int(ymax * height)
        bbox = (xmin, ymin, xmax - xmin, ymax - ymin)
        converted_boxes.append(bbox)

    return converted_boxes

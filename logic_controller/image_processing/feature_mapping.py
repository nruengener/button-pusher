import time

import numpy as np
import cv2

from config import TRACE
from geometry_distance import geometry

MIN_MATCH_COUNT = 3  # 10
FLANN_INDEX_KDTREE = 0

i = 1


def match_keypoints_to_polygon(img1, img2):
    """ Find and match keypoints between two images. Use findHomography to calculate perspective transform. """
    if img1.shape[2] > 0:
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    if img2.shape[2] > 0:
        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    try:
        # Initiate detector
        # det = cv2.xfeatures2d.SIFT_create()
        det = cv2.xfeatures2d.SURF_create()
        # det = cv2.BRISK_create()
        # det = cv2.ORB_create()

        # find the keypoints and descriptors with SURF, ORB or BRISK, SIFT is too slow
        kp1, des1 = det.detectAndCompute(img1, None)
        kp2, des2 = det.detectAndCompute(img2, None)

        # BFMatcher with default params
        bf = cv2.BFMatcher()  # cv2.NORM_HAMMING)
        matches = bf.knnMatch(des1, des2, 2)

        # store all the good matches as per Lowe's ratio test.
        good = []
        for m, n in matches:
            if m.distance < 0.75 * n.distance:  #  0.7
                good.append(m)

        if len(good) > MIN_MATCH_COUNT:
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.LMEDS)  # RANSAC, 5.0
            # M, mask = cv2.findHomography(src_pts, dst_pts, 0)
            matches_mask = mask.ravel().tolist()

            h, w = img1.shape
            pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
            dst = cv2.perspectiveTransform(pts, M)

            if TRACE:
                img2 = cv2.polylines(img2, [np.int32(dst)], True, 255, 3, cv2.LINE_AA)
                # cv2.imshow('poly', img2)

                draw_params = dict(matchColor=(0, 255, 0),  # draw matches in green color
                                   singlePointColor=None,
                                   matchesMask=matches_mask,  # draw only inliers
                                   flags=2)

                img3 = cv2.drawMatches(img1, kp1, img2, kp2, good, None, **draw_params)
                global i
                cv2.imshow("fm" + str(i), img3)
                i = i+1
                cv2.waitKey(0)

            # print(np.int32(dst).reshape((4, 2)))
            return True, np.int32(dst).reshape((4, 2))

        print("Not enough matches are found - ", (len(good) / (MIN_MATCH_COUNT + 1)))
        return False, None

    except Exception:
        print("Exception in feature mapping")
        return False, None


def match_keypoints(img1, img2):
    result_x = -1
    result_y = -1
    if img1.shape[2] > 0:
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    if img2.shape[2] > 0:
        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # Initiate detector
    # sift = cv2.xfeatures2d.SIFT_create()
    # surf = cv2.xfeatures2d.SURF_create()
    # # kaze = cv2.KAZE_create()
    # akaze = cv2.AKAZE_create()
    brisk = cv2.BRISK_create()
    # orb = cv2.ORB_create()

    # todo: test fast?
    # fast = cv2.FastFeatureDetector_create()

    t1 = time.process_time()
    kp2, des2 = brisk.detectAndCompute(img2, None)
    t2 = time.process_time()
    print("brisk pt: ", t2 - t1)

    # find the keypoints and descriptors with ORB or BRISK (brisk seems to be better), SIFT is too slow
    kp1, des1 = brisk.detectAndCompute(img1, None)
    kp2, des2 = brisk.detectAndCompute(img2, None)

    # # match descriptors
    # index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    # search_params = dict(checks=50)
    # flann = cv2.FlannBasedMatcher(index_params, search_params)
    # matches = flann.knnMatch(des1, des2, k=2)

    # BFMatcher with default params
    bf = cv2.BFMatcher()
    t1 = time.process_time()
    matches = bf.knnMatch(des1, des2, k=2)
    t2 = time.process_time()
    print("brute force matcher pt: ", t2 - t1)

    # store all the good matches as per Lowe's ratio test.
    good = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:  #  0.7
            good.append(m)

    if len(good) > MIN_MATCH_COUNT:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.LMEDS)  # RANSAC, 5.0
        # M, mask = cv2.findHomography(src_pts, dst_pts, 0)
        matchesMask = mask.ravel().tolist()

        h, w = img1.shape
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)
        img2 = cv2.polylines(img2, [np.int32(dst)], True, 255, 3, cv2.LINE_AA)

        print(np.int32(dst).reshape((4, 2)))

        result_x, result_y = geometry.centroid_for_polygon(np.int32(dst).reshape((4, 2)))
    else:
        print("Not enough matches are found - ", (len(good) / MIN_MATCH_COUNT))
        matchesMask = None

    draw_params = dict(matchColor=(0, 255, 0),  # draw matches in green color
                       singlePointColor=None,
                       matchesMask=matchesMask,  # draw only inliers
                       flags=2)

    img3 = cv2.drawMatches(img1, kp1, img2, kp2, good, None, **draw_params)
    cv2.imshow("fm", img3)

    return result_x, result_y
    # plt.imshow(img3, 'gray'), plt.show()


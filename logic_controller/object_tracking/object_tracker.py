import time
from threading import Thread

import cv2

from image_processing.feature_mapping import match_keypoints_to_polygon
from geometry_distance.geometry import bounding_box_for_polygon, area_for_polygon


class ObjectTracker:
    """ Create an object tracker which tracks an object through a list of frames """

    def __init__(self, frame_list):
        self.frame_list = frame_list
        # self.tracker = cv2.TrackerMedianFlow_create() KCF  # cv2.TrackerTLD_create() TrackerMOSSE_create
        self.tracker = cv2.TrackerMedianFlow_create()
        self.ok = True
        self.bbox = [0, 0, 0, 0]

    def init_tracker(self, image, bounding_box):
        return self.tracker.init(image, bounding_box)

    def track(self):
        # i = 0
        print("nr of frames: ", len(self.frame_list))
        for frame in self.frame_list:
            self.ok, self.bbox = self.tracker.update(frame)
            if not self.ok:
                return
            # if self.ok:
            #     p1 = (int(self.bbox[0]), int(self.bbox[1]))
            #     p2 = (int(self.bbox[0] + self.bbox[2]), int(self.bbox[1] + self.bbox[3]))
            #     cv2.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)
            # else:
            #     cv2.putText(frame, "Tracking failure detected", (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255),
            #                 2)
            #
            # cv2.imshow('t' + str(i), frame)
            # i = i + 1

    def get_result(self):
        """ return the most recent state and bounding box as well as the last used frame """
        return self.ok, self.bbox

    def set_frame_list(self, frame_list):
        self.frame_list = frame_list


# does not work with video stream, has to be provided with a list of recorded frames
class ThreadedObjectTracker:
    """ Create an object tracking thread """

    def __init__(self, video_stream):
        self.vs = video_stream
        self.vs.start()
        # self.tracker = cv2.TrackerMedianFlow_create()  # cv2.TrackerMIL_create()  # cv2.TrackerTLD_create()
        self.tracker = cv2.TrackerMedianFlow_create()
        self.stopped = False
        self.started = False
        self.ok = True
        self.bbox = [0, 0, 0, 0]
        self.frame = 0

    def init_tracker(self, image, bounding_box):
        return self.tracker.init(image, bounding_box)

    def start(self):
        """ start the thread to read frames from the video stream """
        if not self.started:
            t = Thread(target=self.update, args=())
            t.daemon = True
            t.start()
            self.started = True
        return self

    def update(self):
        """ update tracker with frame from video stream. keep looping infinitely until the thread is stopped """
        while True:
            self.frame = self.vs.read()
            self.ok, self.bbox = self.tracker.update(self.frame)

            # if not self.ok:
            #     print("tf")
            #     self.stop()

            # # Tracking success
            # p1 = (int(self.bbox[0]), int(self.bbox[1]))
            # p2 = (int(self.bbox[0] + self.bbox[2]), int(self.bbox[1] + self.bbox[3]))
            # cv2.rectangle(frame, p1, p2, (255, 0, 0), 2, 1)
            # cv2.imshow("Tracking", frame)

            # exit thread if stopped
            if self.stopped:
                return

    def get_current_state(self):
        """ return the most recent state and bounding box as well as the last used frame """
        return self.ok, self.bbox, self.frame

    def get_current_frame(self):
        return self.vs.read()

    def stop(self):
        self.vs.stop()
        """ indicate that the thread should be stopped """
        self.stopped = True
        self.started = False


class FeatureTracker:
    """ Create a feature mapper which tracks an object by finding and mapping features in two different images """
    def __init__(self, video_stream):
        self.vs = video_stream
        self.vs.start()
        self.stopped = False
        self.started = False
        self.ok = True
        self.roi = 0
        self.bbox = [0, 0, 0, 0]
        self.frame = 0
        self.area = 0

    def init_tracker(self, image, bounding_box):
        self.roi = image[bounding_box[1]:bounding_box[1] + bounding_box[3], bounding_box[0]:bounding_box[0] + bounding_box[2]]
        return True

    def start(self):
        """ start the thread to read frames from the video stream """
        # do nothing as this is not threaded
        # self.update()

    def update(self):
        """ update tracker with frame from video stream. keep looping infinitely until the thread is stopped """
        self.frame = self.vs.read()
        start = time.time()
        self.ok, polygon = match_keypoints_to_polygon(self.roi, self.frame)
        if not self.ok:
            return

        self.area = area_for_polygon(polygon)
        # self.ok = True
        # print("polygon.reshape((1, 8): ", polygon.reshape((1, 8))[0])
        # self.bbox = cv2.minAreaRect(polygon.reshape((1, 8))[0])
        self.bbox = bounding_box_for_polygon(polygon)
        end = time.time()
        print("tracking time taken for one frame: ", end - start)
        # print("bbox: ", self.bbox)
        # self.roi = self.frame[self.bbox[1]:self.bbox[1] + self.bbox[3], self.bbox[0]:self.bbox[0] + self.bbox[2]]
        # cv2.imshow('bbox', self.roi)

    def get_current_state(self):
        """ return the most recent state and bounding box as well as the last used frame """
        self.update()
        return self.ok, self.bbox, self.frame

    def get_current_frame(self):
        return self.vs.read()

    def get_area(self):
        return self.area

    def stop(self):
        self.vs.stop()
        """ indicate that the thread should be stopped """
        self.stopped = True
        self.started = False


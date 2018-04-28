
# modified from source: https://www.pyimagesearch.com/2015/12/28/increasing-raspberry-pi-fps-with-python-and-opencv/

from threading import Thread
from picamera import PiCamera
from picamera.array import PiRGBArray
from config import *


class ListVideoStream:
    """ Thread to capture and store images in a list until stopped """
    def __init__(self, resolution=(CAMERA_WIDTH, CAMERA_HEIGHT),
                 framerate=CAMERA_FRAMERATE, rotation=0,
                 hflip=CAMERA_HFLIP, vflip=CAMERA_VFLIP):
        """ initialize the camera and stream """
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.rotation = rotation
        self.camera.framerate = framerate
        self.camera.hflip = hflip
        self.camera.vflip = vflip
        self.camera.video_stabilization = True  # todo: test HFOV
        self.rawCapture = PiRGBArray(self.camera)  # , size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture,
                                                     format="bgr",
                                                     use_video_port=True)
        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame_list = []
        self.stopped = False

    def start(self):
        """ start the thread to read frames from the video stream """
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        """ keep looping infinitely until the thread is stopped """
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            self.frame_list.append(f.array)
            self.rawCapture.truncate(0)
            # if the thread indicator variable is set, stop the thread
            # and resource camera resources
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return

    def get_frames(self):
        """ return the frame most recently read """
        return self.frame_list

    def stop(self):
        """ indicate that the thread should be stopped """
        self.stopped = True


class PiVideoStream:
    """ Create a Video Stream Thread """
    def __init__(self, resolution=(CAMERA_WIDTH, CAMERA_HEIGHT),
                 framerate=CAMERA_FRAMERATE, rotation=0,
                 hflip=CAMERA_HFLIP, vflip=CAMERA_VFLIP):
        """ initialize the camera and stream """
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.rotation = rotation
        self.camera.framerate = framerate
        self.camera.hflip = hflip
        self.camera.vflip = vflip
        self.camera.video_stabilization = True
        self.rawCapture = PiRGBArray(self.camera)  # , size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture,
                                                     format="bgr",
                                                     use_video_port=True)

        self.frame = None
        # if recording all captured frames are appended to a list
        self.recording = False
        self.frame_list = []
        self.stopped = False

    def start(self):
        """ start the thread to read frames from the video stream """
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def start_recording(self):
        self.recording = True

    def stop_recording(self):
        self.recording = False

    def clean_recordings(self):
        self.frame_list = []

    def get_recordings(self):
        return self.frame_list.copy()  # todo: copy necessary?

    def update(self):
        """ keep looping infinitely until the thread is stopped """
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            self.frame = f.array
            if self.recording:
                self.frame_list.append(self.frame)
            self.rawCapture.truncate(0)
            # if the thread indicator variable is set, stop the thread
            # and resource camera resources
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return

    def read(self):
        """ return the frame most recently read """
        return self.frame

    def stop(self):
        """ indicate that the thread should be stopped """
        self.stopped = True

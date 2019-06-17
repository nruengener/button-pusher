# Pi Camera Settings
CAMERA_WIDTH = 1296  # default= 320 Pi Camera Image width
CAMERA_HEIGHT = 976  # 972   # default= 240 Pi Camera Image width
CAMERA_HFLIP = True  # default= False pi Camera image horiz flip
CAMERA_VFLIP = True  # default= False pi Camera image vert flip
CAMERA_ROTATION = 0  # default= 0  Rotate pi Camera image 0, 90, 180, 270 only valid values
CAMERA_FRAMERATE = 5  # default= 35 framerate of video stream.

F = 3.60  # focal length in mm
HFOV = 53.50  # horizontal field of view in degrees
PIXEL_SIZE = 0.0014  # in mm  (1.4 um)

TOLERANCE_RAD = 0.044  # about 2.5 degrees tolerance for positioning

# DIST_CAM_BASE = 0.133  # distance from camera to base in (x,y)-plane in home position in m
DIST_CAM_BASE = 0.117  # 117  # distance from camera to base in (x,y)-plane in home position in m
DIST_CAM_BASE_START = 0.137
DIST_ENDSTOP_CAM = 0.015  # distance from camera to endstop in (x,y)-plane
DIST_ENDSTOP_CAM_Z = 0.015  # vertical distance from camera to endstop

DEBUG = False
TRACE = False

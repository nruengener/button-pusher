import time

import cv2

from geometry import *
from config import CAMERA_WIDTH, HFOV, DIST_CAM_BASE, DIST_ENDSTOP_CAM, TOLERANCE_RAD, DIST_ENDSTOP_CAM_Z, F

focal_pixel = (CAMERA_WIDTH * 0.5) / math.tan(HFOV * 0.5 * math.pi / 180)


class Movement:
    """ Class for handling movement of robot arm """

    def __init__(self, serial_communication, tracker):
        self.serial_communication = serial_communication
        self.tracker = tracker
        self.dist = DistCalc()
        self.frame = 0
        self.bbox = 0

    def turn_base(self, angle, speed=0):
        """ Blocking call which sends a turn command to the Arduino and waits for the result if command was accepted """
        command = 'G2 X0 Y0 Z{0:.2f} F{1:.2f}'.format(angle * 180.0 / 3.14159, speed)
        print("turn command: ", command)
        response = self.serial_communication.write(command).strip()
        # print("Response from robot: ", response, ". Command was: ", command)
        if response == 'ok':
            # print("waiting for result...")
            response = self.serial_communication.read_until_received("cf", "!!", "er", "or")
            time.sleep(0.2)
            print("Command result: ", response)

    def move_cartesian(self, xmm, ymm, zmm, speed=0):
        """ Blocking call which sends a move command to the Arduino and waits for the result if command was accepted """
        command = 'G1 X{} Y{} Z{} F{}'.format(xmm, ymm, zmm, speed)
        print("cartesian command: ", command)
        response = self.serial_communication.write(command).strip()
        if response == 'ok':
            response = self.serial_communication.read_until_received("cf", "!!", "er", "or")
            time.sleep(0.2)
            print("Command result: ", response)
        else:
            print("move err response: ", response)
            print("received: ", self.serial_communication.read_all())

    def move_home(self):
        response = self.serial_communication.write('H0')
        if response == 'ok':
            response = self.serial_communication.read_until_received("cf", "!!", "er", "or")
            time.sleep(0.1)
            print("Command result: ", response)
        else:
            print("move home err response: ", response)
            print("received: ", self.serial_communication.read_all())

    def get_distance_by_moving(self, image, bounding_box):
        """ Try to determine the distance to the target by moving the arm. """
        angle_to_ver, angle_to_hor = calculate_angles_from_center(image, bounding_box, focal_pixel)
        # initialize tracker
        self.tracker.init_tracker(image, bounding_box)
        self.tracker.start()

        if abs(angle_to_ver) > TOLERANCE_RAD:
            print("Going to turn base to get distances.")
            ok = self.get_distance_by_turning()
            if not ok:
                print("Could not determine distance by turning base.")
                return False
        elif abs(angle_to_hor) > TOLERANCE_RAD:
            print("trying to center vertically")
            # ver = self.center_vertically(image, bounding_box)  todo: implement
            return False
        else:
            print("angle_to_ver: ", angle_to_ver, "angle_to_hor: ", angle_to_hor)
            print("move towards target to calculate distance")
            # todo: implement
            return False

        return True

    def move_to_target(self):
        """ Move to the currently selected bounding box. The distance is calculated by first moving a fraction of the
        guessed distance towards the target and calculating the distance by changed size of object. """
        if self.dist.distance_to_cam <= 0:
            return False

        angle_to_ver, angle_to_hor = calculate_angles_from_center(self.frame, self.bbox, focal_pixel)
        h1 = self.bbox[3]
        b1 = self.bbox[2]
        area1 = self.tracker.area
        z_diff = calculate_height(self.dist.distance_to_cam, angle_to_hor)
        print("z diff: ", z_diff)
        print("angle_to_ver: ", angle_to_ver, ", angle_to_hor: ", angle_to_hor)

        z_mm = (z_diff + DIST_ENDSTOP_CAM_Z) * 1000
        x_mm = self.dist.get_x1mm()
        y_mm = self.dist.get_y1mm()  # (self.dist.distance_to_base - DIST_CAM_BASE - DIST_ENDSTOP_CAM) * 1000
        print("xmm: ", x_mm, ", ymm: ", y_mm, ", zmm: ", z_mm)

        # move part of the way and check if target can be tracked
        self.move_cartesian(x_mm / 3, y_mm / 3, z_mm / 2)
        # self.move_cartesian(x_mm, y_mm, z_mm)
        # time.sleep(0.2)

        ok, self.bbox, self.frame = self.tracker.get_current_state()
        if not ok:
            print("Tracking Error")
            return False

        distance_1 = distance(x_mm, y_mm, z_mm)
        print("distance first calculated (to endstop): ", distance_1)

        angle_to_ver, angle_to_hor = calculate_angles_from_center(self.frame,self.bbox, focal_pixel)
        print("angle_to_ver2: ", angle_to_ver, ", angle_to_hor2: ", angle_to_hor)

        # calculate distance by change of area
        distance_travelled = distance(x_mm / 3, y_mm / 3, z_mm / 2)
        distance_travelled_xy = math.sqrt((x_mm / 3) * (x_mm / 3) + (y_mm / 3) * (y_mm / 3))
        print("distance travelled: ", distance_travelled)
        print("distance distance_travelled_xy: ", distance_travelled_xy)

        h2 = self.bbox[3]
        b2 = self.bbox[2]
        area2 = self.tracker.area

        g2 = calc_g2(distance_travelled, h1, h2)
        d_xyz = g2 + distance_travelled
        print("h1: ", h1, ", h2: ", h2)
        print("g2: ", g2)
        print("g2_2: ", calc_g22(F, distance_travelled, h1, h2))
        print("distance now calculated (to cam): ", distance_travelled + g2)

        print("area1: ", area1, ", area2: ", area2, ", area1 / (area2 - area1): ", area1 / (area2 - area1))
        print("b1: ", b1, ", b2: ", b2, ", b1 / (b2 - b1): ", b1 / (b2 - b1))

        # calculate new values for xmm, ymm and zmm
        d_z = d_xyz * math.sin(angle_to_ver)
        d_xy = d_xyz * math.cos(angle_to_ver)
        epsilon = math.atan2(x_mm / 3, y_mm / 3)  # angle in (x,y)-plane resulting by movement
        # todo: signs?
        d_x = d_xy * math.sin(self.dist.beta + epsilon + angle_to_hor)
        d_y = d_xy * math.cos(self.dist.beta + epsilon + angle_to_hor)
        print("new values xmm: ", d_x, ", ymm: ", d_y, ", zmm: ", d_z)
        return True

    def get_distance_by_turning(self):
        """ Try to calculate distances by turning the base by a defined angle. Tracker has to be initialized. """
        ok, self.bbox, self.frame = self.tracker.get_current_state()
        if not ok:
            print("Tracking Error")
            return False

        self.dist.alpha1, angle_to_hor = calculate_angles_from_center(self.frame, self.bbox, focal_pixel)

        if abs(self.dist.alpha1) < TOLERANCE_RAD:
            print("Within tolerance. Not going to turn.")
            return False

        # init tracking and turn for 2 degrees
        self.dist.beta = 0.035 if self.dist.alpha1 > 0 else -0.035
        # self.dist.beta = 0.043 if self.dist.alpha1 > 0 else -0.043
        self.turn_base(self.dist.beta, 8)
        # track after turning
        ok, self.bbox, self.frame = self.tracker.get_current_state()
        if not ok:
            print("Tracking Error")
            return False

        # get new angles to center
        self.dist.alpha2, angle_to_hor_new = calculate_angles_from_center(self.frame, self.bbox, focal_pixel)
        # calculate angle to center image horizontally
        self.dist.turning_angle, self.dist.distance_to_base, self.dist.distance_to_cam = calculate_turning_angle(
            self.dist.beta, self.dist.alpha1,
            self.dist.alpha2, DIST_CAM_BASE)

        return True

    def center_horizontally(self, image, bounding_box):
        """ Try to center the image horizontally on the center of the target bounding box """
        # calculate the angles from the center with the focal length in pixels
        center_of_bb = (bounding_box[0] + bounding_box[2] / 2, bounding_box[1] + bounding_box[3] / 2)
        angle_to_ver, angle_to_hor = calculate_angles_from_center(image, center_of_bb[0], center_of_bb[1],
                                                                focal_pixel)
        print("angle to ver: ", angle_to_ver)
        if abs(angle_to_ver) < TOLERANCE_RAD:
            print("Within tolerance. Not going to center horizontally.")
            return False

        # init tracking and turn for two degrees
        self.tracker.init_tracker(image, bounding_box)
        self.tracker.start()
        self.dist.beta = 0.035 if angle_to_ver > 0 else -0.035
        # beta = 0.04 if angle_to_ver > 0 else -0.04
        # beta = 0.05236 if angle_to_ver > 0 else -0.05236

        self.turn_base(self.dist.beta, 8)
        ok, bbox, frame = self.tracker.get_current_state()
        if not ok:
            print("Tracking Error")
            return False

        x, y = (int(bbox[0] + bbox[2] / 2), int(bbox[1] + bbox[3] / 2))
        if x < 0 or y < 0:
            return False

        cv2.circle(frame, (x, y), 5, 255, 3)
        cv2.imshow('tracked center after first turn', frame)

        # get new angles to center
        angle_to_ver_new, angle_to_hor_new = calculate_angles_from_center(frame, x, y, focal_pixel)
        print("new angle to ver: ", angle_to_ver_new)

        # calculate angle to center image horizontally
        turning_angle, distance_to_base, distance_to_cam = calculate_turning_angle(self.beta, angle_to_ver, angle_to_ver_new,
                                                                                   DIST_CAM_BASE)
        if angle_to_ver_new < 0 < turning_angle or turning_angle < 0 < angle_to_ver_new:
            turning_angle = -turning_angle

        print("angle to turn: ", turning_angle)
        print("distance to base: ", distance_to_base)
        print("distance to cam: ", distance_to_cam)

        # todo: calculate height and return values to move directly (in center method)?
        # todo: use another method for this (move_to_target)
        height = calculate_height(distance_to_cam, angle_to_hor_new)
        print("height: ", height)
        z_mm = (height + DIST_ENDSTOP_CAM_Z) * 1000
        x_mm = distance_to_cam * math.sin(angle_to_ver_new) * 1000  # todo: sign? should be ok as angle 0 < |angle| < pi
        y_mm = (distance_to_base - DIST_CAM_BASE - DIST_ENDSTOP_CAM) * 1000

        # move part of the way and check if target can be tracked
        self.move_cartesian(x_mm // 3, y_mm // 3, z_mm // 3)
        time.sleep(0.2)

        ok, bbox, frame = self.tracker.get_current_state()
        if not ok:
            print("Tracking Error")
            return False

        x, y = (int(bbox[0] + bbox[2] / 2), int(bbox[1] + bbox[3] / 2))
        if x < 0 or y < 0:
            return False

        angle_to_ver_new, angle_to_hor_new = calculate_angles_from_center(frame, x, y, focal_pixel)

        print("new distance to cam: ", distance_to_base - DIST_CAM_BASE)
        # angle_to_ver, angle_to_hor = calculate_angles_to_center(new_image, center_of_bb[0], center_of_bb[1],
        #                                                         focal_pixel)
        # height = calculate_height(distance_to_base - DIST_CAM_BASE, angle_to_hor_new)  # todo: height can be calculated before move
        # print("height: ", height)

        # todo: forward move in x,y plane - how to know which direction in x and y
        # distance_mm = (distance_to_base - DIST_CAM_BASE - DIST_ENDSTOP_CAM) * 1000
        # self.move_cartesian(0, distance_mm, height * 1000)

        # x, y = match_keypoints(roi, new_image)
        # if x < 0 or y < 0:
        #     return False
        #
        # cv2.circle(new_image, (x, y), 5, 255, 3)
        cv2.imshow('Finish', frame)
        time.sleep(1)
        return True

    def center_on_target(self, image, bounding_box):
        """ Try to center the image on the center of the target bounding box. """
        center_of_bb = (bounding_box[0] + bounding_box[2] / 2, bounding_box[1] + bounding_box[3] / 2)
        angle_to_ver, angle_to_hor = calculate_angles_from_center(image, center_of_bb[0], center_of_bb[1],
                                                                focal_pixel)
        # initialize tracker
        self.tracker.init_tracker(image, bounding_box)
        self.tracker.start()

        if abs(angle_to_ver) > TOLERANCE_RAD:
            print("Going to center horizontally.")
            hor = self.center_horizontally(image, bounding_box)  # todo: return values?
            if not hor:
                return False
        elif abs(angle_to_hor) > TOLERANCE_RAD:
            print("trying to center vertically")
            # ver = self.center_vertically(image, bounding_box)  todo: implement
        else:
            print("move towards target to calculate distance")

        return True


# class MovementOld:
#     """ Class for handling movement of arm """
#
#     def __init__(self, serial_communication, video_stream):
#         self.serial_communication = serial_communication
#         self.video_stream = video_stream
#
#     def turn_base(self, angle):
#         """ Blocking call which sends a turn command to the Arduino and waits for the result if command was accepted """
#         command = 'G2 X0 Y0 Z{0:.2f}'.format(angle * 180.0 / 3.14159)
#         response = self.serial_communication.write(command).strip()
#         print("Response from robot: ", response, ". Command was: ", command)
#         # response = response.strip()
#
#         if response == 'ok':
#             print("waiting for result...")
#             response = self.serial_communication.read_until_received("cf", "!!", "er", "or")
#             time.sleep(0.2)
#             print("Command result: ", response)
#
#     def move_cartesian(self, xmm, ymm, zmm):
#         """ Blocking call which sends a move command to the Arduino and waits for the result if command was accepted """
#         command = 'G1 X{} Y{} Z{}'.format(xmm, ymm, zmm)
#         response = self.serial_communication.write(command).strip()
#         if response == 'ok':
#             response = self.serial_communication.read_until_received("cf", "!!", "er", "or")
#             time.sleep(0.2)
#             print("Command result: ", response)
#         else:
#             print("move err response: ", response)
#
#     def center_on_target(self, image, bounding_box, ):
#         """ Try to center the image on the center of the target bounding box """
#         # calculate the angles from the center with the focal length in pixels
#         center_of_bb = (bounding_box[0] + bounding_box[2] / 2, bounding_box[1] + bounding_box[3] / 2)
#         angle_to_ver, angle_to_hor = calculate_angles_to_center(image, center_of_bb[0], center_of_bb[1],
#                                                                 focal_pixel)
#
#         print("angle to ver: ", angle_to_ver)
#         # todo: center vert method and use only if abs(angle) > TOLERANCE_RAD
#
#         # first turn by a defined angle
#         # zmm = 5 if angle_to_hor > 0 else -5
#         # todo: only turn if |angle| > 0.035 or so ?
#         beta = 0.035 if angle_to_ver > 0 else -0.035  # two degrees
#         self.video_stream.start_recording()
#         self.turn_base(beta)
#         self.video_stream.stop_recording()
#
#         frame_list = self.video_stream.get_recordings()
#         self.video_stream.clean_recordings()
#         tracker = ObjectTracker(frame_list)  # self.tracker.update(self.frame)
#         t1 = time.process_time()
#         tracker.init_tracker(image, bounding_box)
#         tracker.track()
#         t2 = time.process_time()
#         print("tracking pt: ", t2 - t1)
#
#         ok, bbox = tracker.get_result()
#         new_image = self.video_stream.read()
#
#         ok = False
#
#         if ok:
#             x, y = (int(bbox[0] + bbox[2] / 2), int(bbox[1] + bbox[3] / 2))
#         else:
#             # use tracker to get new center of moved target
#             roi = image[bounding_box[1]:bounding_box[1] + bounding_box[3],
#                   bounding_box[0]:bounding_box[0] + bounding_box[2]]
#             # use keypoint matcher (provided trackers like KFC, MIL etc. do not work properly cause of vibration)
#             x, y = match_keypoints(roi, new_image)
#
#         if x < 0 or y < 0:
#             return False
#
#         cv2.circle(new_image, (x, y), 5, 255, 3)
#         cv2.imshow('Center', new_image)
#
#         # get new angles to center
#         angle_to_ver_new, angle_to_hor_new = calculate_angles_to_center(new_image, x, y, focal_pixel)
#         print("new angle to ver: ", angle_to_ver_new)
#
#         # beta_new = beta * 1 / ((angle_to_ver - angle_to_ver_new) / angle_to_ver)
#         # self.turn_base(beta_new)
#
#         # todo: calculate distance from camera to base (in x,y plane)???
#         # todo: or only operate from home position (so it is 130mm)
#         # todo: is base (0,0)?
#         # calculate angle to center image horizontally
#         turning_angle, distance_to_base, distance_to_cam = calculate_turning_angle(beta, angle_to_ver, angle_to_ver_new,
#                                                                                    DIST_CAM_BASE)
#         if angle_to_ver_new < 0 < turning_angle or turning_angle < 0 < angle_to_ver_new:
#             turning_angle = -turning_angle
#
#         print("angle to turn: ", turning_angle)
#         print("distance to base: ", distance_to_base)
#
#         # todo: track continuously if fast enough
#         self.video_stream.start_recording()
#         self.turn_base(turning_angle)
#         self.video_stream.stop_recording()
#
#         # todo: track and get new angles
#         print("new distance to cam: ", distance_to_base - DIST_CAM_BASE)
#         # angle_to_ver, angle_to_hor = calculate_angles_to_center(new_image, center_of_bb[0], center_of_bb[1],
#         #                                                         focal_pixel)
#         height = calculate_height(distance_to_base - DIST_CAM_BASE,
#                                   angle_to_hor_new)  # todo: this is the old angle, use new after centering horizontally
#         print("height: ", height)
#
#         # todo: forward move in x,y plane - how to know which direction in x and y
#         distance_mm = (distance_to_base - DIST_CAM_BASE - DIST_ENDSTOP_CAM) * 1000
#         self.move_cartesian(0, distance_mm, height * 1000)
#
#         new_image = self.video_stream.read()
#         # x, y = match_keypoints(roi, new_image)
#         # if x < 0 or y < 0:
#         #     return False
#         #
#         # cv2.circle(new_image, (x, y), 5, 255, 3)
#         cv2.imshow('Finish', new_image)
#
#         return True


class DistCalc:
    """ Helper class for distance calculations """

    def __init__(self, cam_to_base=DIST_CAM_BASE):
        """ initialize the camera and stream """
        self.beta = 0  # angle turned towards target
        self.alpha1 = 0  # angle to camera before turning
        self.alpha2 = 0  # angle to camera after turning by beta
        self.cam_to_base = cam_to_base  # length from base center to cam in (x,y)-plane
        self.turning_angle = 0  # angle needed to turn base to center target after first turn by beta
        self.distance_to_base = 0  # distance from base to target in (x,y)-plane
        self.distance_to_cam = 0  # distance from camera to target in (x,y)-plane

    def get_y1mm(self):
        """ gets the distance on the y axis to the target in mm after first turning """
        ly = self.distance_to_base * math.cos(self.beta + self.turning_angle)
        return (ly - self.cam_to_base - DIST_ENDSTOP_CAM) * 1000

    def get_x1mm(self):
        """ gets the distance on the x axis to the target in mm after first turning """
        print("self.distance_to_base: ", self.distance_to_base)
        print("self.cam_to_base: ", self.cam_to_base)
        print("self.beta: ", self.beta)
        print("self.turning_angle: ", self.turning_angle)
        c = abs(self.cam_to_base * math.sin(self.beta))
        lx = abs(self.distance_to_base * math.sin(self.beta + self.turning_angle))
        print("lx: ", lx)
        print("c: ", c)
        return (lx - c) * 1000 * np.sign(self.turning_angle)

    # def get_zmm(self):
    #     z_diff = calculate_height(self.dist.distance_to_cam, angle_to_hor)
    #     z_mm = (height + DIST_ENDSTOP_CAM_Z) * 1000
    #     x_mm = distance_to_cam * math.sin(angle_to_ver_new) * 1000  # todo: sign? should be ok as angle 0 < |angle| < pi
    #     y_mm = (distance_to_base - DIST_CAM_BASE - DIST_ENDSTOP_CAM) * 1000

import time

import cv2

from geometry import *
from config import CAMERA_WIDTH, HFOV, DIST_CAM_BASE, DIST_ENDSTOP_CAM, TOLERANCE_RAD, DIST_ENDSTOP_CAM_Z, F, \
    DIST_CAM_BASE_START

focal_pixel = (CAMERA_WIDTH * 0.5) / math.tan(HFOV * 0.5 * math.pi / 180)


class Movement:
    """ Class for handling movement of robot arm """

    def __init__(self, serial_communication, tracker):
        self.serial_communication = serial_communication
        self.tracker = tracker
        self.frame = 0
        self.bbox = [0, 0, 0, 0]

    def turn_base(self, angle, speed=0):
        """ Blocking call which sends a turn command to the Arduino and waits for the result if command was accepted """
        command = 'G2 X0 Y0 Z{0:.2f} F{1:.2f}'.format(angle * 180.0 / 3.14159, speed)
        print("turn command: ", command)
        response = self.serial_communication.write(command).strip()
        # print("Response from robot: ", response, ". Command was: ", command)
        if response == 'ok':
            # print("waiting for result...")
            response = self.serial_communication.read_until_received("cf", "!!", "er", "or", "rs")
            time.sleep(0.2)
            print("Command result: ", response)
        else:
            print("turn err response: ", response)
            print("received: ", self.serial_communication.read_all())

    def move_cartesian(self, xmm, ymm, zmm, speed=0):
        """ Blocking call which sends a move command to the Arduino and waits for the result if command was accepted """
        command = 'G1 X{} Y{} Z{} F{}'.format(xmm, ymm, zmm, speed)
        print("cartesian command: ", command)
        response = self.serial_communication.write(command).strip()
        if response == 'ok':
            response = self.serial_communication.read_until_received("cf", "!!", "er", "or", "rs")
            if response == 'er':
                print("Endstop reached! Moving to home position.")
                response = self.serial_communication.read_until_received("cf", "!!", "or")
                print(response)
                print("comments received: ", self.serial_communication.read_all())
            # print("comments from robot arm: ", self.serial_communication.read_all())
            time.sleep(0.2)
            print("Command result: ", response)
        else:
            print("move err response: ", response)
            print("received: ", self.serial_communication.read_all())

    def move_home(self):
        response = self.serial_communication.write('H0')
        if response == 'ok':
            response = self.serial_communication.read_until_received("cf", "!!", "er", "or", "rs")
            print("comments from robot arm: ", self.serial_communication.read_all())
            time.sleep(0.2)
            print("Command result: ", response)
        else:
            print("move home err response: ", response)
            print("received: ", self.serial_communication.read_all())

    def move_to_target(self, image, bounding_box):
        """ Try to determine the distance to the target by moving the arm. """
        # initialize tracker
        self.tracker.init_tracker(image, bounding_box)
        self.tracker.start()
        self.frame = image
        self.bbox = bounding_box

        ok, dx, dy, dz = self.move_sideways()
        if not ok:
            print("Tracking Error")
            return False

        h1 = self.bbox[3]
        b1 = self.bbox[2]
        if dx == 0 and dy == 0 and dz == 0:
            print("not moved because within tolerance of angles")
            dx = 0
            dz = 0
            dy = 30

        dx3 = dx / 3
        dy3 = dy / 3
        dz3 = dz / 3
        # self.move_cartesian(dx3, dy3, dz3)

        # todo: remove test
        self.move_cartesian(dx, dy, dz + DIST_ENDSTOP_CAM_Z * 1000)
        return True

        ok, self.bbox, self.frame = self.tracker.get_current_state()
        if not ok:
            print("Tracking Error")
            return False

        # calculate distance by change of B
        distance_travelled = distance(dx3, dy3, dz3)
        h2 = self.bbox[3]
        b2 = self.bbox[2]

        g2 = calc_g2(distance_travelled, h1, h2)
        d_xyz = g2 + distance_travelled
        print("h1: ", h1, ", h2: ", h2)
        print("distance_travelled: ", distance_travelled)
        print("g2: ", g2)
        print("rest distance (to cam): ", distance(dx, dy, dz))
        print("distance now calculated (to cam): ", d_xyz)

        print("b1: ", b1, ", b2: ", b2, ", b1 / (b2 - b1): ", b1 / (b2 - b1))

        return True

    def move_sideways(self):
        """ Try to determine the distance to the target by moving the arm sideways.
        Returns the remaining distances on the axes. """
        angle_to_ver1, angle_to_hor1 = calculate_angles_from_center(self.frame, self.bbox, focal_pixel)
        # first move by a defined distance on  x and z axis
        if -TOLERANCE_RAD < angle_to_ver1 < TOLERANCE_RAD:
            x1 = 0
        else:
            x1 = 15.0 if angle_to_ver1 > 0 else -15.0
        if -TOLERANCE_RAD < angle_to_hor1 < TOLERANCE_RAD:
            z1 = 0
        else:
            z1 = 10 if angle_to_hor1 > 0 else -10

        if x1 == 0 and z1 == 0:
            return True, 0, 0, 0

        # todo: move result (e.g. moving error, timeout ...) and return False if no success
        self.move_cartesian(x1, 0, z1, 50)

        ok, self.bbox, self.frame = self.tracker.get_current_state()
        if not ok:
            print("Tracking Error")
            return False, 0, 0, 0

        x1 = 0.89 * x1  # failure in movement
        z1 = 0.89 * z1
        x_cam = x1 * (DIST_CAM_BASE_START / (DIST_CAM_BASE_START + DIST_ENDSTOP_CAM))
        print("x1: ", x1, ", x_cam: ", x_cam)

        angle_to_ver2, angle_to_hor2 = calculate_angles_from_center(self.frame, self.bbox, focal_pixel)

        # angle that base has turned
        beta = math.atan2(x_cam, DIST_CAM_BASE_START * 1000)
        print("turning angle (beta): ", beta)
        # angle from the y axis to the target
        angle_to_ver_c = angle_to_ver2 + beta
        print("angle from y axis to target after move: ", angle_to_ver_c)

        if abs(angle_to_ver2 - angle_to_ver1) < TOLERANCE_RAD:
            x2 = 0
        else:
            x2c = x1 * math.tan(angle_to_ver_c) / (math.tan(angle_to_ver1) - math.tan(angle_to_ver_c))
            x2 = x2c - (x1 - x_cam)

        # as the camera does not turn on z axis there is no need to calculate a different angle here
        if abs(angle_to_hor2 - angle_to_hor1) < TOLERANCE_RAD:
            z2 = 0
        else:
            z2 = z1 * math.tan(angle_to_hor2) / (math.tan(angle_to_hor1) - math.tan(angle_to_hor2))
        # if angle_to_hor2 < 0:
        #         z2 = -z2

        y = abs((x1 + x2) / math.tan(angle_to_ver1))
        y_z = abs((z1 + z2) / math.tan(angle_to_hor1))
        if y == 0:
            y = y_z

        print("x2: ", x2, ", z2: ", z2, ", y: ", y, ", y_z: ", y_z)
        return True, x2, y, z2

    # todo: change
    def move_to_target_old(self):
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

        # calculate distance by change of B
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



import math
import numpy as np

from config import PIXEL_SIZE, CAMERA_WIDTH, CAMERA_HEIGHT, HFOV


def calculate_angles_from_center_p(image_np, x, y, f):
    """ calculate the angles from the center of the image to a point.
    f is the focal length in pixels """
    h, w, d = image_np.shape
    center = np.array([0, 0, f])
    pixel_hor = np.array([x - w / 2, 0, f])  # ([x - w/2, y - h/2, f])
    dot = np.dot(center, pixel_hor)
    angle_to_ver = math.acos(dot / (length(center) * length(pixel_hor)))
    if x < w / 2:
        angle_to_ver = -angle_to_ver

    pixel_ver = np.array([0, y - h / 2, f])
    dot = np.dot(center, pixel_ver)
    angle_to_hor = math.acos(dot / (length(center) * length(pixel_ver)))
    if y > h / 2:  # y starts at the top
        angle_to_hor = -angle_to_hor

    return angle_to_ver, angle_to_hor


def calculate_angles_from_center(image_np, bbox, f):
    """ calculate the angles from the center of the image to a point.
    f is the focal length in pixels """
    x, y = (bbox[0] + bbox[2] / 2, bbox[1] + bbox[3] / 2)
    h, w, d = image_np.shape

    center = np.array([0, 0, f])
    pixel_hor = np.array([x - w / 2, 0, f])  # ([x - w/2, y - h/2, f])
    dot = np.dot(center, pixel_hor)
    angle_to_ver = math.acos(dot / (length(center) * length(pixel_hor)))
    print("angle with vectors: ", angle_to_ver)

    # method from bachelor thesis:
    # alpha = math.atan(math.tan(math.radians(HFOV/2)) * abs(x - w / 2) / (w / 2))
    # print("angle with hfov: ", alpha)

    if x < w / 2:
        angle_to_ver = -angle_to_ver

    pixel_ver = np.array([0, y - h / 2, f])
    dot = np.dot(center, pixel_ver)
    angle_to_hor = math.acos(dot / (length(center) * length(pixel_ver)))
    if y > h / 2:  # y starts at the top
        angle_to_hor = -angle_to_hor

    print("angle_to_ver: ", angle_to_ver, ", angle_to_hor: ", angle_to_hor)

    return angle_to_ver, angle_to_hor


def calculate_angles_to_center(image_np, x, y, f):
    """ calculate the angles from a point to the horizontal and vertical middle lines.
    f is the focal length in pixels """
    h, w, d = image_np.shape
    center = np.array([0, 0, f])
    pixel_hor = np.array([x - w / 2, 0, f])  # ([x - w/2, y - h/2, f])
    dot = np.dot(center, pixel_hor)
    angle_to_ver = math.acos(dot / (length(center) * length(pixel_hor)))
    if x > w / 2:
        angle_to_ver = -angle_to_ver

    pixel_ver = np.array([0, y - h / 2, f])
    dot = np.dot(center, pixel_ver)
    angle_to_hor = math.acos(dot / (length(center) * length(pixel_ver)))
    if y > h / 2:
        angle_to_hor = -angle_to_hor

    return angle_to_ver, angle_to_hor


def calculate_h(alpha1, alpha2, zmm):
    """ Calculate the height from old center of image after moving for z mm on the z-axis """
    if alpha1 - alpha2 < 0.1 or alpha1 - alpha2 > -0.1:
        return 0
    x = math.sin(alpha1) / math.sin(alpha2)
    print(x)
    if x == 1:
        return 0
    h = (-x / (1 - x)) * zmm
    print(h)
    return h


def calculate_height(distance, angle):
    """ Calculate the height from camera to the target using the distance from the camera to the target and the angle. """
    # if angle < 0:
    #     angle = -angle
    return distance * math.tan(angle)


def calculate_turning_angle(beta, alpha1, alpha2, cam_to_base_m):
    """ Calculate the remaining angle to turn the base to get the camera in line with the target (horizontally).
    As the camera is not centered on the base the angle is different from the camera's angle. """
    print("winkel: ", beta, ", ", alpha1, ", ", alpha2)
    beta = abs(beta)
    diff_sign = np.sign(alpha1) != np.sign(alpha2)
    sign_alpha2 = np.sign(alpha2)
    alpha1 = abs(alpha1)
    alpha2 = abs(alpha2)

    # cam_to_base_m = cam_to_base_mm / 1000

    c = math.sqrt(2 * cam_to_base_m * cam_to_base_m * (1 - math.cos(beta)))
    delta = (math.pi - beta) / 2
    epsilon = math.pi - alpha1 - delta
    # gamma = abs(2 * delta + alpha1 - alpha2 - math.pi)
    if diff_sign:
        gamma = 2 * delta + alpha1 + alpha2 - math.pi
    else:
        gamma = 2 * delta + alpha1 - alpha2 - math.pi

    print("c: ", c)
    print("delta: ", delta)
    print("epsilon: ", epsilon)
    print("gamma: ", gamma)

    if gamma < 0:
        print("Failure in calculating turning angle!")
    distance_to_cam = c * math.sin(epsilon) / math.sin(gamma)  # distance to cam
    print("distance to cam: ", distance_to_cam)

    # kosinussatz
    distance_to_base = math.sqrt(cam_to_base_m * cam_to_base_m + distance_to_cam * distance_to_cam - 2 * cam_to_base_m * distance_to_cam * math.cos(math.pi - alpha2))
    turning_angle = sign_alpha2 * math.asin(math.sin(math.pi - alpha2) * distance_to_cam / distance_to_base)
    print("turning_angle: ", turning_angle)
    return turning_angle, distance_to_base, distance_to_cam


def length(np_array):
    # return np.sqrt((np_array * np_array).sum(axis=1))
    return np.sqrt((np_array * np_array).sum(axis=0))


def centroid_for_polygon(polygon):
    area = area_for_polygon(polygon)
    if area == 0:
        print(polygon)
        return -1, -1

    imax = len(polygon) - 1

    result_x = 0
    result_y = 0
    for i in range(0, imax):
        result_x += (polygon[i][0] + polygon[i + 1][0]) * (
                    (polygon[i][0] * polygon[i + 1][1]) - (polygon[i + 1][0] * polygon[i][1]))
        result_y += (polygon[i][1] + polygon[i + 1][1]) * (
                    (polygon[i][0] * polygon[i + 1][1]) - (polygon[i + 1][0] * polygon[i][1]))
    result_x += (polygon[imax][0] + polygon[0][0]) * (
                (polygon[imax][0] * polygon[0][1]) - (polygon[0][0] * polygon[imax][1]))
    result_y += (polygon[imax][1] + polygon[0][1]) * (
                (polygon[imax][0] * polygon[0][1]) - (polygon[0][0] * polygon[imax][1]))
    result_x /= (area * 6.0)
    result_y /= (area * 6.0)

    return int(result_x), int(result_y)  # {'x': result_x, 1: result_y}


def area_for_polygon(polygon):
    result = 0
    imax = len(polygon) - 1
    for i in range(0, imax):
        result += (polygon[i][0] * polygon[i + 1][1]) - (polygon[i + 1][0] * polygon[i][1])
    result += (polygon[imax][0] * polygon[0][1]) - (polygon[0][0] * polygon[imax][1])
    return abs(result / 2.0)


def bounding_box_for_polygon(polygon):
    if len(polygon) < 4:
        return [0, 0, 0, 0]
    x1 = (polygon[0][0] + polygon[1][0]) // 2
    y1 = (polygon[0][1] + polygon[3][1]) // 2
    x2 = (polygon[2][0] + polygon[3][0]) // 2
    y2 = (polygon[1][1] + polygon[2][1]) // 2
    if x1 < 0:
        x1 = 0
    if x2 > CAMERA_WIDTH:
        x2 = CAMERA_WIDTH
    if y1 < 0:
        y1 = 0
    if y2 > CAMERA_HEIGHT:
        y2 = CAMERA_HEIGHT
    w = (x2 - x1)
    h = (y2 - y1)
    return x1, y1, w, h


def area_for_bounding_box(bbox):
    polygon = [(bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), (bbox[0], bbox[3])]
    result = 0
    imax = len(polygon) - 1
    for i in range(0, imax):
        result += (polygon[i][0] * polygon[i + 1][1]) - (polygon[i + 1][0] * polygon[i][1])
    result += (polygon[imax][0] * polygon[0][1]) - (polygon[0][0] * polygon[imax][1])
    return result / 2.


def distance(dx, dy, dz):
    return math.sqrt(dx*dx + dy*dy + dz*dz)


def calc_g2(dd, h1, h2):
    """ Calculate distance by using distance difference and object sizes"""
    return dd * h1 / (h2 - h1)


def calc_g22(f, d, h1, h2):
    """ Calculate distance by using distance difference and object sizes"""
    # convert pixel tom mm (on sensor)
    B1 = h1 * PIXEL_SIZE
    B2 = h2 * PIXEL_SIZE
    print("B1: ", B1, ", B2: ", B2)
    return (B1 * (d - f) + B2 * f) / (B2 - B1)


def get_distances_on_axes(d_xyz, angle_to_ver, angle_to_hor):
    """ Calculate distances on axes to the target """
    z = math.sin(angle_to_hor) * d_xyz  # without endstop distance to cam on z axis
    d_xy = math.cos(angle_to_hor) * d_xyz
    x = math.sin(angle_to_ver) * d_xy
    y = math.cos(angle_to_ver) * d_xy
    return x, y, z


center_factor_h = 0.16
center_factor_w = 0.25

area_factor = 0.75


def filter_tokens(tokens, image_np):
    """
    Filter tokens by size, position ...
    Tokens are in format x1, y1, x2, y2.
    :param tokens: The tokens to filter.
    :param image_np: The image that contains the tokens.
    :return: The filtered tokens.
    """

    filtered = []
    height, width = image_np.shape[:2]
    area = height * width
    for t in tokens:
        w = t[2] - t[0]
        h = t[3] - t[1]
        # sort out if token is almost as big as roi
        if w * h > area * area_factor:
            continue

        if h > height * 0.9:
            continue

        # sort out if token too small  # todo: use height instead?
        # if w * h < area * 0.03:
        if h < height * 0.3:
            continue

        # keep if roughly centered
        if roughly_centered(t, image_np):
            filtered.append(t)

    # todo: sort out outer tokens if tokens in tokens (but in filtered list)?
    for t in filtered:
        remove = False
        for to in filtered:
            if token_contains_token(t, to):
                print("box in box")
                filtered.remove(to)
        #         remove = True
        #         break
        #
        # if remove:
        #     filtered.remove(t)  # todo: possible? check if concurrent exception else use second list

    # filtered = sorted(filtered, key=lambda token: token[0])
    return sorted(filtered, key=lambda token: token[0])


def roughly_centered(bbox, image_np):
    """ Check if the given bounding box is roughly (expressed by center_factor) centered in the image """
    h, w = image_np.shape[:2]
    x = (bbox[0] + bbox[2]) / 2
    y = (bbox[1] + bbox[3]) / 2
    center_x = w / 2
    center_y = h / 2
    c_h = center_x - w * center_factor_w < x < center_x + w * center_factor_w  # not so strict cause of two digits
    c_v = center_y - h * center_factor_h < y < center_y + h * center_factor_h
    return c_h and c_v


def contains(r1, r2):
    """ Return true if rectangle r1 contains r2 """
    return r1.x1 < r2.x1 < r2.x2 < r1.x2 and r1.y1 < r2.y1 < r2.y2 < r1.y2


def box_contains_box(b1, b2):
    """ Returns true if b1 contains b2 """
    return b1[0] < b2[0] < b2[0] + b2[2] < b1[0] + b1[2] and b1[1] < b2[1] < b2[1] + b2[3] < b1[1] + b1[3]


def token_contains_token(b1, b2):
    """ Returns true if b1 contains b2 """
    # w = t[2] - t[0]
    # h = t[3] - t[1]
    return b1[0] < b2[0] < b2[2] < b1[2] and b1[1] < b2[1] < b2[3] < b1[3]


center_factor = 0.16

area_factor = 0.9


def filter_tokens(tokens, image_np):
    filtered = []
    if len(image_np.shape) > 2:
        h, w, _ = image_np.shape
    else:
        h, w = image_np.shape
    area = h * w
    for t in tokens:
        # sort out if token is almost as big as roi
        if area - t[2] * t[3] > area * area_factor:
            continue

        # sort out if token too small
        if t[2] * t[3] < area * 0.05:
            continue

        # keep if roughly centered
        if roughly_centered(t, image_np):
            filtered.append(t)

    # todo: sort out outer tokens if tokens in tokens (but in filtered list)?
    for t in filtered:
        remove = False
        for to in filtered:
            if box_contains_box(t, to):
                remove = True
                break

        if remove:
            filtered.remove(t)  # todo: possible? check if concurrent ex... else use second list

    return filtered


def roughly_centered(bbox, image_np):
    """ Check if the given bounding box is roughly (expressed by center_factor) centered in the image """
    if len(image_np.shape) > 2:
        h, w, _ = image_np.shape
    else:
        h, w = image_np.shape
    x = (bbox[0] + bbox[2]) / 2
    y = (bbox[1] + bbox[3]) / 2
    center_x = w / 2
    center_y = h / 2
    c_h = center_x - w * center_factor * 2 < x < center_x + w * center_factor * 2  # not so strict cause of two digits
    c_v = center_y - h * center_factor < y < center_y + h * center_factor
    return c_h and c_v


def contains(r1, r2):
    """ Return true if rectangle r1 contains r2 """
    return r1.x1 < r2.x1 < r2.x2 < r1.x2 and r1.y1 < r2.y1 < r2.y2 < r1.y2


def box_contains_box(b1, b2):
    """ Returns true if b1 contains b2 """
    return b1[0] < b2[0] < b2[0] + b2[2] < b1[0] + b1[2] and b1[1] < b2[1] < b2[1] + b2[3] < b1[1] + b1[3]
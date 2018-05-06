from __future__ import print_function  # python3 style print
import os
import numpy as np

from button_detection import label_map_util
from button_detection import visualization_utils as vis_util

CURRENT_ABS_PATH = os.path.dirname(os.path.abspath(__file__))
PATH_TO_LABELS = os.path.join(CURRENT_ABS_PATH, 'button_model', 'object-detection.pbtxt')
# PATH_TO_TEXT_LABELS = os.path.join(CURRENT_ABS_PATH, 'button_text_model', 'object-detection-button-labels.pbtxt')

NUM_CLASSES = 1  # only elevator button

# Loading label map
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES,
                                                            use_display_name=True)
category_index = label_map_util.create_category_index(categories)

THRESHOLD = 0.5


def detect_buttons(image_np, sess, detection_graph):
    """
       Detect objects in the given image. Return image with rois and array with boxes where score is above threshold 0.5.
    """

    # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
    image_np_expanded = np.expand_dims(image_np, axis=0)
    image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

    # Each box represents a part of the image where a particular object was detected.
    boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

    # Each score represent how level of confidence for each of the objects.
    # Score is shown on the result image, together with the class label.
    scores = detection_graph.get_tensor_by_name('detection_scores:0')
    classes = detection_graph.get_tensor_by_name('detection_classes:0')
    num_detections = detection_graph.get_tensor_by_name('num_detections:0')

    # Actual detection.
    (boxes, scores, classes, num_detections) = sess.run(
        [boxes, scores, classes, num_detections],
        feed_dict={image_tensor: image_np_expanded})

    # Visualization of the results of a detection.
    vis_util.visualize_boxes_and_labels_on_image_array(
        image_np,
        np.squeeze(boxes),
        np.squeeze(classes).astype(np.int32),
        np.squeeze(scores),
        category_index,
        use_normalized_coordinates=True,
        line_thickness=4)

    boxes_thres = []
    for i, b in enumerate(np.squeeze(boxes)):
        if np.squeeze(scores)[i] > THRESHOLD:
            print("box: ", b, ", score: ", np.squeeze(scores)[i], "i: ", i)
            boxes_thres.append(b)

    print("Detected ", len(boxes_thres), " with score > ", THRESHOLD)

    return image_np, boxes_thres


# Loading label map
# label_map_text = label_map_util.load_labelmap(PATH_TO_TEXT_LABELS)
# categories_text = label_map_util.convert_label_map_to_categories(label_map_text, max_num_classes=NUM_CLASSES, use_display_name=True)
# category_index_labels = label_map_util.create_category_index(categories_text)
#
#
# def detect_button_labels(image_np, sess, detection_graph):
#     """
#        Detect objects in the given image. Return image with rois and array with boxes where score is above threshold 0.5.
#     """
#
#     # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
#     image_np_expanded = np.expand_dims(image_np, axis=0)
#     image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
#
#     # Each box represents a part of the image where a particular object was detected.
#     boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
#
#     # Each score represent how level of confidence for each of the objects.
#     # Score is shown on the result image, together with the class label.
#     scores = detection_graph.get_tensor_by_name('detection_scores:0')
#     classes = detection_graph.get_tensor_by_name('detection_classes:0')
#     num_detections = detection_graph.get_tensor_by_name('num_detections:0')
#
#     # Actual detection.
#     (boxes, scores, classes, num_detections) = sess.run(
#         [boxes, scores, classes, num_detections],
#         feed_dict={image_tensor: image_np_expanded})
#
#     # Visualization of the results of a detection.
#     vis_util.visualize_boxes_and_labels_on_image_array(
#         image_np,
#         np.squeeze(boxes),
#         np.squeeze(classes).astype(np.int32),
#         np.squeeze(scores),
#         category_index_labels,
#         use_normalized_coordinates=True,
#         line_thickness=4,
#         min_score_thresh=.5)
#
#     boxes_thres = []
#     for i, b in enumerate(np.squeeze(boxes)):
#         if np.squeeze(scores)[i] > 0.5:
#             print("box: ", b, ", score: ", np.squeeze(scores)[i], "i: ", i)
#             boxes_thres.append(b)
#
#     print("Detected ", len(boxes_thres), " with score > 0.5")
#     print("scores: ", scores)
#
#     return image_np, boxes_thres

import os
import tensorflow as tf
import numpy as np
from button_detection import visualization_utils as vis_util, label_map_util

CURRENT_ABS_PATH = os.path.dirname(os.path.abspath(__file__))

# button model
PATH_TO_CKPT = os.path.join(CURRENT_ABS_PATH, 'button_model', 'frozen_inference_graph.pb')
PATH_TO_LABELS = os.path.join(CURRENT_ABS_PATH, 'button_model', 'object-detection.pbtxt')
NUM_CLASSES = 1  # only elevator button

# threshold for detect button probability
THRESHOLD = 0.5

# Loading label map todo: remove
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES,
                                                            use_display_name=True)
category_index = label_map_util.create_category_index(categories)


class ButtonDetector:
    """ Class for detecting buttons with a tensorflow session and the detection graph """

    def __init__(self):
        # setup button detection graph
        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

                config = tf.ConfigProto()
                config.gpu_options.allow_growth = True
                config.gpu_options.per_process_gpu_memory_fraction = 0.5
                self.sess_detection = tf.Session(graph=self.detection_graph, config=config)  # button detection session

    def detect_buttons(self, image_np):
        """
          Detect objects in the given image.
          Return image with rois and array with boxes where score is above the threshold.
        """

        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(image_np, axis=0)
        image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')

        # Each box represents a part of the image where a particular object was detected.
        boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')

        # Each score represent how level of confidence for each of the objects.
        # Score is shown on the result image, together with the class label.
        scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
        classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
        num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')

        # Actual detection.
        (boxes, scores, classes, num_detections) = self.sess_detection.run(
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

        print("Detected ", len(boxes_thres), " buttons with score > ", THRESHOLD)

        return image_np, boxes_thres

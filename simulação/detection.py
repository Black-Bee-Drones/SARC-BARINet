import tensorflow as tf
import cv2 as cv


# print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
global sess


def start_detection():
    with tf.io.gfile.GFile('./rcnn/frozen_inference_graph.pb', 'rb') as f:
        graph_def = tf.compat.v1.GraphDef()
        graph_def.ParseFromString(f.read())

    global sess
    sess = tf.compat.v1.Session()
    sess.graph.as_default()
    tf.import_graph_def(graph_def, name='')


def detect(img):
    # Read and preprocess an image.
    # img = cv.imread('ssd/example3.jpg')
    rows = img.shape[0]
    cols = img.shape[1]
    inp = cv.resize(img, (300, 300))
    inp = inp[:, :, [2, 1, 0]]  # BGR2RGB

    # print('Running Model')
    # Run the model
    out = sess.run([sess.graph.get_tensor_by_name('num_detections:0'),
                    sess.graph.get_tensor_by_name('detection_scores:0'),
                    sess.graph.get_tensor_by_name('detection_boxes:0'),
                    sess.graph.get_tensor_by_name('detection_classes:0')],
                   feed_dict={'image_tensor:0': inp.reshape(1, inp.shape[0], inp.shape[1], 3)})

    # print('Visualizing boxes')
    # Visualize detected bounding boxes.
    num_detections = int(out[0][0])
    if num_detections == 0:
        return None

    else:
        for i in range(num_detections):
            score = float(out[1][0][i])
            bbox = [float(v) for v in out[2][0][i]]
            if score > 0.6:
                x = bbox[1] * cols
                y = bbox[0] * rows
                right = bbox[3] * cols
                bottom = bbox[2] * rows
                rectangle = [[int(x), int(y)], [int(right), int(bottom)]]
                return rectangle

        return None

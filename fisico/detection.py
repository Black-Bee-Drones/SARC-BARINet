import numpy as np
import tensorflow as tf
import cv2 as cv
import time

#print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

def start_detection():
    with tf.io.gfile.GFile('./rcnn/frozen_inference_graph.pb', 'rb') as f:
        graph_def = tf.compat.v1.GraphDef()
        graph_def.ParseFromString(f.read())
    
    global sess
    sess = tf.compat.v1.Session()
    sess.graph.as_default()
    tf.import_graph_def(graph_def, name='')

def detect(img, precision):
    # Read and preprocess an image.
    #img = cv.imread('ssd/example3.jpg')
    results = []
    max = 0
    rows = img.shape[0]
    cols = img.shape[1]
    inp = cv.resize(img, (300, 300))
    inp = inp[:, :, [2, 1, 0]]  # BGR2RGB

    #print('Running Model')
    # Run the model
    out = sess.run([sess.graph.get_tensor_by_name('num_detections:0'),
                    sess.graph.get_tensor_by_name('detection_scores:0'),
                    sess.graph.get_tensor_by_name('detection_boxes:0'),
                    sess.graph.get_tensor_by_name('detection_classes:0')],
                    feed_dict={'image_tensor:0': inp.reshape(1, inp.shape[0], inp.shape[1], 3)})

    #print('Visualizing boxes')
    # Visualize detected bounding boxes.
    num_detections = int(out[0][0])
    if num_detections == 0:
        return None
    
    else:
        for i in range(num_detections):
            classId = int(out[3][0][i])
            score = float(out[1][0][i])

            if score > precision:
                if score > max:
                    max = score
                    idx = i
            
        if max > precision:
            bbox = [float(v) for v in out[2][0][idx]]
            x = bbox[1] * cols
            y = bbox[0] * rows
            right = bbox[3] * cols
            bottom = bbox[2] * rows
            rectangle = [[int(x), int(y)], [int(right), int(bottom)], max]
            return rectangle

        return None

import numpy as np
import tensorflow as tf
import cv2 as cv
import time

print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

# Read the graph.
with tf.io.gfile.GFile('./rcnn/frozen_inference_graph.pb', 'rb') as f:
    graph_def = tf.compat.v1.GraphDef()
    graph_def.ParseFromString(f.read())

# Load image
#cap = cv.VideoCapture(0)
cap = cv.VideoCapture('./videos/video_focos_incendio_2.mp4')
    
with tf.compat.v1.Session() as sess:
    # Restore session
    sess.graph.as_default()
    tf.import_graph_def(graph_def, name='')

    while cap.isOpened():
        #time.sleep(5)
        ret, frame = cap.read()
        # Read and preprocess an image.
        #img = cv.imread('ssd/example3.jpg')
        img = frame
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
        for i in range(num_detections):
            classId = int(out[3][0][i])
            score = float(out[1][0][i])
            bbox = [float(v) for v in out[2][0][i]]
            if score > 0.8:
                x = bbox[1] * cols
                y = bbox[0] * rows
                right = bbox[3] * cols
                bottom = bbox[2] * rows
                cv.rectangle(img, (int(x), int(y)), (int(right), int(bottom)), (125, 255, 51), thickness=2)

        # Show results
        img = cv.resize(img, (1280, 720))
        cv.imshow('TensorFlow RCNN', img)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv.destroyAllWindows()
import cv2
import numpy as np
import detection
import time

def nothing():
  pass

cv2.namedWindow('Janela')
cv2.createTrackbar('precision', 'Janela', 75, 100, nothing)

cap = cv2.VideoCapture(1)

detection.start_detection()

if (cap.isOpened()== False): 
  print("Error opening video stream or file")

while(cap.isOpened()):
  ret, frame = cap.read()

  if ret == True:

    precision = cv2.getTrackbarPos('precision','Janela')/100

    start = time.time()
    results = detection.detect(frame, precision)

    if results is not None:
        print(results)
        cv2.rectangle(frame, (results[0][0], results[0][1]), (results[1][0], results[1][1]), (125, 255, 51), thickness=2)
        cv2.putText(frame, "{:.2f}".format(results[2]), (results[0][0], results[0][1]), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,0,0), 2)

    end = time.time()
    fps = 1 / (end-start)
    print("FPS: ", "{:.2f}".format(fps))

    cv2.imshow('Janela', frame)

    # Press Q on keyboard to  exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break

  else: 
    break

cap.release()
cv2.destroyAllWindows()
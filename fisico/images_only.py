import cv2
import numpy as np
#import detection
import time

cap = cv2.VideoCapture(1)

#detection.start_detection()

while(cap.isOpened()):
  ret, frame = cap.read()

  if ret == True:

    cv2.imshow('Janela', frame)

    # Press Q on keyboard to  exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break

  else: 
    break

cap.release()
cv2.destroyAllWindows() 
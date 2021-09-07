import cv2
import os

dir = r'./videos'
num_video = 0
num_frame = 0

for filename in os.listdir(dir):
    file = os.fsdecode(filename)
    if filename.endswith(".mp4"): 
        num_video += 1
        video = os.path.join(dir, file)
        print(video)
        cap = cv2.VideoCapture(video)

        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret:
                num_frame += 1
                cv2.imshow('frame', frame)
                if num_frame % 20 == 0:
                    img_name = './imgs/video'+str(num_video)+'img'+str(int(num_frame/20))+'.png'
                    print(img_name)
                    cv2.imwrite(img_name, frame)
                if cv2.waitKey(1) == ord('q'):
                    break
            else:
                break
    else:
        pass
    
cap.release()
cv2.destroyAllWindows()
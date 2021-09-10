import airsim
import os
import cv2
import numpy as np

# connect to the AirSim simulator
client = airsim.MultirotorClient()

while True:
    print("connecting")
    responses = client.simGetImages([airsim.ImageRequest(0, airsim.ImageType.Scene, True)])
    response = responses[0]

    # get numpy array
    img1d = np.fromstring(response.image_data_uint8, dtype=np.uint8) 

    # reshape array to 4 channel image array H X W X 4
    img_rgb = img1d.reshape(response.height, response.width, 3)

    cv2.imshow('tela', img_rgb)
    k = cv2.waitKey(1)
    #if k == 0:
    #    cv2.closeAllWindows()
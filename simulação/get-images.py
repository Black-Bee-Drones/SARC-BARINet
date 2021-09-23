import airsim
import cv2
import numpy as np
import time

# connect to the AirSim simulator
client = airsim.MultirotorClient()


def get_image(drone_num):
    drone_name = 'Drone' + str(drone_num)
    responses = client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)],
                                    vehicle_name=drone_name)
    return responses[0]


def show_img():
    for i in range(3):
        response = get_image(i + 1)
        # get numpy array
        img1d = np.fromstring(response.image_data_uint8, dtype=np.uint8)
        # reshape array to 4 channel image array H X W X 4
        img_rgb = img1d.reshape(response.height, response.width, 3)

        window_name = 'Janela' + str(i)

        cv2.imshow(window_name, img_rgb)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return True


while True:
    start = time.time()

    if show_img():
        break

    end = time.time()
    fps = 1 / (end - start)
    print("FPS: ", "{:.2f}".format(fps))

cv2.destroyAllWindows()

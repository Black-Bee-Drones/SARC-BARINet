#!/usr/bin/env python3
import asyncio
from mavsdk import System
from mavsdk.offboard import (OffboardError, VelocityBodyYawspeed)
from satellite_imagery import get_satellite_image
import cv2
import time
import detection

# Definição do drone 1 como variável global para poder utilizar em qualquer função assíncrona
drone = System()
altitude = 3
found = -1
qntd = 0
precision = 0.4
camera_num = 1


async def get_lat_lng(dr):  # Define a função para pegar a posição do drone
    async for position in dr.telemetry.position():
        return [position.latitude_deg, position.longitude_deg]


async def main():
    # Nesse programa a função de movimentação é dependente da função da camera e no momento que "encontrar fogo" a
    # task de movimentação é cancelada
    cam = asyncio.create_task(camera())
    await cam

    # New trajeto é a função de "o que ele vai fazer depois de encontrar fogo?"

    if found:
        new_trajeto = asyncio.create_task(found_fire())
        await new_trajeto

    end = asyncio.create_task(end_mission())
    await end


async def movimentacao_drone():
    global drone

    # Drone se conecta
    # await drone.connect(system_address="udp://:14540")
    await drone.connect(system_address="serial://COM3:57600")

    print("Waiting for drone 1 to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"Drone discovered!")
            break

    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok:
            print("Global position estimate ok")
            break

    # Arma o drone
    print("-- Arming")
    await drone.action.arm()

    await drone.action.set_takeoff_altitude(altitude)  # Configura a altitude de decolagem para 3 m
    print("-- Taking off")
    await drone.action.takeoff()
    await asyncio.sleep(8)

    print("-- Setting offboard initial setpoint")  # Configura as velocidades relativas atuais como 0
    await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))

    print("-- Starting offboard")
    try:
        await drone.offboard.start()
    except OffboardError as error:
        print(f"Starting offboard mode failed with error code: \
              {error._result.result}")
        print("-- Disarming")
        return

    # Gira 360 graus
    print('Rotating. . .')
    await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0, 0, 0, 20))


# Função da camera
async def camera():
    global found, qntd
    global precision, camera_num

    detection.start_detection()

    drone_fly = asyncio.create_task(movimentacao_drone())
    await asyncio.sleep(4)

    cap = cv2.VideoCapture(camera_num)

    if cap.isOpened() is False:
        print("Error opening video stream or file")

    while cap.isOpened():
        ret, frame = cap.read()

        if ret:
            start = time.time()
            results = detection.detect(frame, precision)

            if results is not None:
                qntd += 1
                if qntd == 3:
                    qntd = 0
                    print(results)
                    cv2.rectangle(frame, (results[0][0], results[0][1]), (results[1][0], results[1][1]), (125, 255, 51),
                                  thickness=2)
                    cv2.putText(frame, "{:.2f}".format(results[2]), (results[0][0], results[0][1]),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                    print("Found fire . . .")
                    cv2.imwrite('fire.png', frame)
                    found = 1

            end = time.time()
            fps = 1 / (end - start)
            print("FPS: ", "{:.2f}".format(fps))

            cv2.imshow('Window', frame)

            # Press Q on keyboard to  exit
            await asyncio.sleep(0.2)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Keyboard Interruption . . .")
                found = 0

            if found != -1:
                asyncio.Task.cancel(drone_fly)
                break

        else:
            break

    await drone.action.hold()
    await asyncio.sleep(3)
    cap.release()
    cv2.destroyAllWindows()


# Trajeto que será feito após a detecção de fogo
async def found_fire():
    global drone

    print("Getting satellite image")
    get_satellite_image(await get_lat_lng(drone))


async def end_mission():
    global drone

    print("-- Stopping offboard")
    try:
        await drone.offboard.stop()
    except OffboardError as error:
        print(f"Stopping offboard mode failed with error code: \
              {error._result.result}")

    await drone.action.set_return_to_launch_altitude(altitude)
    print("-- Returning to launch and landing")
    await drone.action.return_to_launch()

    # Pousa o drone
    print("-- Landing")
    await drone.action.land()
    await asyncio.sleep(8)

    # Desarma o drone
    print("Disarming. . .")
    await drone.action.disarm()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

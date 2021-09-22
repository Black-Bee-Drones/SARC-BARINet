#!/usr/bin/env python3
import asyncio
from mavsdk import System
from mavsdk.offboard import (OffboardError, VelocityBodyYawspeed)
from satellite_imagery import get_satellite_image
import cv2
import numpy as np
import airsim
import time
import detection

# Definição do drone 3 como variável global para poder utilizar em qualquer função assíncrona

global drone3

drone3 = System(mavsdk_server_address='localhost', port=50042)

async def movimentacao_drone3():

    cam = asyncio.create_task(camera3())

    # Drone se conecta
    await drone3.connect(system_address="udp://:14542")

    print("Waiting for drone 3 to connect...")
    async for state in drone3.core.connection_state():
        if state.is_connected:
            print(f"Drone 3 discovered!")
            break

    # Setando valores iniciais para o offboard
    print("-- Setting initial setpoint")
    await drone3.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))

    # Iniciando o Offboard
    try:
        await drone3.offboard.start()
    except OffboardError as error:
        print(f"Start Drone 3 offboard failed with error code: {error._result.result}")
        print("-- Drone 3  Disarming")
        await drone3.action.disarm()
        return

    # Drone arma
    print("-- Arming")
    await drone3.action.arm()

    print("-- Takeoff")
    await drone3.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, -5.0, -14))
    await asyncio.sleep(15)

    print("-- Mission Drone 3")
    # Indo pra frente. . .
    await drone3.offboard.set_velocity_body(VelocityBodyYawspeed(5, 0, 0, 0))
    await asyncio.sleep(43)

    # Subindo. . .
    await drone3.offboard.set_velocity_body(VelocityBodyYawspeed(0, 0, -4, 0))
    await asyncio.sleep(10)

    # Dando uma giradinha
    await drone3.offboard.set_velocity_body(VelocityBodyYawspeed(0, 0, 0, -27, ))
    await asyncio.sleep(20)

    # Para o offboard
    print("-- Stopping offboard")
    try:
        await drone3.offboard.stop()
    except OffboardError as error:
        print(f"Stopping offboard mode failed with error code: \
              {error._result.result}")

    #  Para a funçao camera rodando em segundo plano
    await asyncio.Task.cancel(camera3())

    print("-- Returning to Launch")
    await drone3.action.return_to_launch()
    await asyncio.sleep(20)


async def camera3():

    client = airsim.MultirotorClient()

    detection.start_detection()

    while True:
        start = time.time()
        responses = client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)],
                                        vehicle_name='Drone3')
        response = responses[0]
        img1d = np.fromstring(response.image_data_uint8, dtype=np.uint8)
        img_rgb = img1d.reshape(response.height, response.width, 3)

        results = detection.detect(img_rgb)

        if results is not None:
            print(results)
            cv2.rectangle(img_rgb, (results[0][0], results[0][1]), (results[1][0], results[1][1]), (125, 255, 51),
                          thickness=2)
            await asyncio.create_task(coordenadas())

        end = time.time()
        fps = 1 / (end - start)
        print("FPS: ", "{:.2f}".format(fps))

        cv2.imshow('Janela', img_rgb)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            asyncio.Task.cancel(drone3_fly)
            break

        await asyncio.sleep(0.1)

    cv2.destroyAllWindows()

async def coordenadas(): #Funcão que printa as coordenadas lat e long e imagens satelite
    
    async for parametros in drone3.telemetry.position():
        latitude = parametros.latitude_deg
        longitude = parametros.longitude_deg
        break

    print(f'\nFIRE!! FIRE !! ')
    print(f'LATITUDE:','{:.5f}'.format(latitude))
    print(f'LONGITUDE:','{:.5f}\n'.format(longitude))

    print("Getting satellite image")
    await asyncio.create_task(get_satellite_image([latitude,longitude]))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(movimentacao_drone3())

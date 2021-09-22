#!/usr/bin/env python3
import asyncio
from mavsdk import System
from mavsdk.offboard import (OffboardError, VelocityBodyYawspeed)
from satellite_imagery import get_satellite_image
import cv2
import airsim
import numpy as np
import time
import detection

# Definição do drone 1 como variável global para poder utilizar em qualquer função assíncrona

global drone1

drone1 = System(mavsdk_server_address='localhost', port=50040)

async def movimentacao_drone1():

    cam = asyncio.create_task(camera1())
    
    # Drone se conecta
    await drone1.connect(system_address="udp://:14540")

    print("Waiting for drone 1 to connect...")
    async for state in drone1.core.connection_state():
        if state.is_connected:
            print(f"Drone 1 discovered!")
            break

    # Setando valores iniciais para o aoffboard
    print("-- Setting initial setpoint")
    await drone1.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))

    # Iniciando o Offboard
    try:
        await drone1.offboard.start()
    except OffboardError as error:
        print(f"Start Drone 1 offboard failed with error code: {error._result.result}")
        print("-- Drone 1  Disarming")
        await drone1.action.disarm()
        return

    # Drone arma
    print("-- Arming")
    await drone1.action.arm()

    print("-- Takeoff")
    await drone1.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, -6.0, -7))
    await asyncio.sleep(15)

    print("-- Mission Drone 1")
    # da uma giradinha e vai pra tras
    await drone1.offboard.set_velocity_body(VelocityBodyYawspeed(4, 0, 0, 0))
    await asyncio.sleep(15)

    # Primeira curva
    await drone1.offboard.set_velocity_body(VelocityBodyYawspeed(7, 0, -1, 28))
    await asyncio.sleep(6)
    await drone1.offboard.set_velocity_body(VelocityBodyYawspeed(4, 0, 0, 0))
    await asyncio.sleep(22)

    # Segunda curva
    await drone1.offboard.set_velocity_body(VelocityBodyYawspeed(7, 0, -1, -28))
    await asyncio.sleep(6)
    await drone1.offboard.set_velocity_body(VelocityBodyYawspeed(4, 0, 0, 0))
    await asyncio.sleep(30)

    # Terceira curva
    await drone1.offboard.set_velocity_body(VelocityBodyYawspeed(7, 0, -1, 28))
    await asyncio.sleep(6)
    await drone1.offboard.set_velocity_body(VelocityBodyYawspeed(4, 0, 0, 0))
    await asyncio.sleep(18)

    # Quarta Curva
    await drone1.offboard.set_velocity_body(VelocityBodyYawspeed(7, 0, -1, -28))
    await asyncio.sleep(6)

    # Subindo 70m
    await drone1.offboard.set_velocity_body(VelocityBodyYawspeed(0, 0, -5, 0))
    await asyncio.sleep(14)

    # Girando
    await drone1.offboard.set_velocity_body(VelocityBodyYawspeed(0, 0, 0, 63))
    await asyncio.sleep(3)

    # PARA PARA PARA PARA PARA
    await drone1.offboard.set_velocity_body(VelocityBodyYawspeed(0, 0, 0, 0))
    await asyncio.sleep(5)

    # Girando de volta
    await drone1.offboard.set_velocity_body(VelocityBodyYawspeed(0, 0, 0, -63))
    await asyncio.sleep(3)

    # Indo pra frente
    await drone1.offboard.set_velocity_body(VelocityBodyYawspeed(4, 0, 0, 00))
    await asyncio.sleep(15)

    # Para o offboard
    print("-- Stopping offboard")
    try:
        await drone1.offboard.stop()
    except OffboardError as error:
        print(f"Stopping offboard mode failed with error code: \
              {error._result.result}")

    #  Para a funçao camera rodando em segundo plano
    await asyncio.Task.cancel(camera1())

    print("-- Returning to Launch")
    await drone1.action.return_to_launch()
    await asyncio.sleep(15)


async def camera1():

    client = airsim.MultirotorClient()

    detection.start_detection()

    while True:
        start = time.time()
        responses = client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)],
                                        vehicle_name='Drone1')
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
            break

        await asyncio.sleep(0.1)

    cv2.destroyAllWindows()

async def coordenadas(): #Funcão que printa as coordenadas lat e long e imagens satelite
    
    async for parametros in drone1.telemetry.position():
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
    loop.run_until_complete(movimentacao_drone1())

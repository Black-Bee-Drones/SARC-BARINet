#!/usr/bin/env python3
import asyncio
from mavsdk import System
from mavsdk.offboard import (OffboardError, VelocityBodyYawspeed)
import cv2
import airsim
import numpy as np
import time
import detection

# Definição do drone 1 como variável global para poder utilizar em qualquer função assíncrona

global drone2

drone2 = System(mavsdk_server_address='localhost', port=50041)

async def movimentacao_drone2():

    cam = asyncio.create_task(camera2())

    # Drone se conecta
    await drone2.connect(system_address="udp://:14541")

    print("Waiting for drone 2 to connect...")
    async for state in drone2.core.connection_state():
        if state.is_connected:
            print(f"Drone 2 discovered!")
            break

    # Setando valores iniciais para o offboard
    print("-- Setting initial setpoint")
    await drone2.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))

    # Iniciando o Offboard
    try:
        await drone2.offboard.start()
    except OffboardError as error:
        print(f"Start Drone 1 offboard failed with error code: {error._result.result}")
        print("-- Drone 1  Disarming")
        await drone2.action.disarm()
        return

    # Drone arma
    print("-- Arming")
    await drone2.action.arm()

    print("-- Takeoff")
    await drone2.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, -6.0, 7))
    await asyncio.sleep(15)

    await drone2.offboard.set_velocity_body(VelocityBodyYawspeed(0, 0, 0, 0))
    await asyncio.sleep(3)

    await drone2.offboard.set_velocity_body(VelocityBodyYawspeed(4, 0, 0, 0))
    await asyncio.sleep(15)

    print("Primeira curva")
    await drone2.offboard.set_velocity_body(VelocityBodyYawspeed(7, 0, -1, 28))
    await asyncio.sleep(6)
    await drone2.offboard.set_velocity_body(VelocityBodyYawspeed(4, 0, 0, 0))
    await asyncio.sleep(22)

    print("Segunda curva")
    await drone2.offboard.set_velocity_body(VelocityBodyYawspeed(7, 0, -1, -28))
    await asyncio.sleep(6)
    await drone2.offboard.set_velocity_body(VelocityBodyYawspeed(4, 0, -2, 0))
    await asyncio.sleep(22)

    print("Subindo. . .")
    await drone2.offboard.set_velocity_body(VelocityBodyYawspeed(0, 0, -2, 0))
    await asyncio.sleep(10)

    print("Terceira curva")
    await drone2.offboard.set_velocity_body(VelocityBodyYawspeed(7, 0, -1, 28))
    await asyncio.sleep(6)
    await drone2.offboard.set_velocity_body(VelocityBodyYawspeed(4, 0, 0, 0))
    await asyncio.sleep(22)

    print("Voltando para o ponto inicial")
    await drone2.offboard.set_position_ned(PositionNedYaw(0, 0, -60, 0))
    await asyncio.sleep(25)

    # Para o offboard
    print("-- Stopping offboard")
    try:
        await drone2.offboard.stop()
    except OffboardError as error:
        print(f"Stopping offboard mode failed with error code: \
              {error._result.result}")

    await drone2.action.return_to_launch()
    await asyncio.sleep(15)


async def camera2():

    client = airsim.MultirotorClient()

    detection.start_detection()

    while True:
        start = time.time()
        responses = client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)],
                                        vehicle_name='Drone2')
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

async def coordenadas(): #Funcão que printa as coordenadas lat e long
    
    async for parametros in drone2.telemetry.position():
        latitude = parametros.latitude_deg
        longitude = parametros.longitude_deg
        break

    print(f'\nFIRE!! FIRE !! ')
    print(f'LATITUDE:','{:.5f}'.format(latitude))
    print(f'LONGITUDE:','{:.5f}\n'.format(longitude))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(movimentacao_drone2())

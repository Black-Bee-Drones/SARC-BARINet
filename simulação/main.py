"""
[ x ] Definir a home

[ x ] Decolar e ir para o ponto de início

[   ] Detectar fogo (ajuda da galera da detecção)

[ x ] Cameras tirando fotos

[ ? ] Movimentar o drone em uma área pré-definida

[   ] Enviar as coordenadas para a GroundStation

[   ] Retorno ao ponto de home
"""

import asyncio
import airsim
import cv2
from mavsdk import System
from mavsdk.offboard import (VelocityBodyYawspeed)


async def run():
    drone1 = System(mavsdk_server_address="localhost", port=50040)
    drone2 = System(mavsdk_server_address="localhost", port=50041)
    drone3 = System(mavsdk_server_address="localhost", port=50042)

    await drone1.connect(system_address="udp://:14540")
    await drone2.connect(system_address="udp://:14541")
    await drone3.connect(system_address="udp://:14542")

    print("Waiting for drone 1 to connect...")
    async for state in drone1.core.connection_state():
        if state.is_connected:
            print(f"Drone 1 discovered!")
            break

    print("Waiting for drone 2 to connect...")
    async for state in drone2.core.connection_state():
        if state.is_connected:
            print(f"Drone 2 discovered!")
            break

    print("Waiting for drone 3 to connect...")
    async for state in drone3.core.connection_state():
        if state.is_connected:
            print(f"Drone 3 discovered!")
            break

    # Drones armam

    print("-- Arming")
    await drone1.action.arm()

    print("-- Arming 2 ")
    await drone2.action.arm()

    print("-- Arming 3 ")
    await drone3.action.arm()

    # Drones decolam
    print("-- Takeoff")
    await drone1.action.takeoff()

    print("-- Takeoff 2")
    await drone2.action.takeoff()

    print("-- Takeoff 3")
    await drone3.action.takeoff()

    # Começa a tirar as fotos dos 3 drones
    print("Starting taking photos. . .")
    asyncio.ensure_future(camera1())
    asyncio.ensure_future(camera2())
    asyncio.ensure_future(camera3())

    # Drones decolam
    print("-- Taking off")
    await drone1.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, -2.0, 0.0))
    await drone2.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, -2.0, 0.0))
    await drone3.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, -2.0, 0.0))
    await asyncio.sleep(8)

    # Drones esperam 2 segundos
    print("-- Wait for a bit")
    await drone1.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
    await drone2.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
    await drone3.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
    await asyncio.sleep(2)

    # Drones rotacionam em direção aos pontos de início
    print("-- Rotating")
    await drone1.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, 0.0, 30.0))
    await drone2.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
    await drone3.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, 0.0, -30.0))
    await asyncio.sleep(3)

    # Drones das extremidades se distanciam 600 metros do central
    print("-- Going to the first waypoint")
    await drone1.offboard.set_velocity_body(
        VelocityBodyYawspeed(10.0, 0.0, 0.0, 0.0))
    await drone2.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, 0.0, 6.0))
    await drone3.offboard.set_velocity_body(
        VelocityBodyYawspeed(10.0, 0.0, 0.0, 0.0))
    await asyncio.sleep(60)

    # Drones esperam 2 segundos e reajustam suas posições
    print("-- Wait for a bit")
    await drone1.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, 0.0, -30.0))
    await drone2.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
    await drone3.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, 0.0, 30.0))
    await asyncio.sleep(2)

    # Drones começam a patrulha
    print("-- Starting patrol")
    await drone1.offboard.set_velocity_body(
        VelocityBodyYawspeed(10.0, 0.0, 0.0, 6.0))
    await drone2.offboard.set_velocity_body(
        VelocityBodyYawspeed(10.0, 0.0, 0.0, 6.0))
    await drone3.offboard.set_velocity_body(
        VelocityBodyYawspeed(10.0, 0.0, 0.0, 6.0))
    await asyncio.sleep(60)

    # Drones vão 180m para frente
    print("-- Going to the second waypoint")
    await drone1.offboard.set_velocity_body(
        VelocityBodyYawspeed(10.0, 0.0, 0.0, 0.0))
    await drone2.offboard.set_velocity_body(
        VelocityBodyYawspeed(10.0, 0.0, 0.0, 6.0))
    await drone3.offboard.set_velocity_body(
        VelocityBodyYawspeed(10.0, 0.0, 0.0, 0.0))
    await asyncio.sleep(18)

    # Drones começam a patrulha
    print("-- Starting patrol")
    await drone1.offboard.set_velocity_body(
        VelocityBodyYawspeed(10.0, 0.0, 0.0, 6.0))
    await drone2.offboard.set_velocity_body(
        VelocityBodyYawspeed(10.0, 0.0, 0.0, 6.0))
    await drone3.offboard.set_velocity_body(
        VelocityBodyYawspeed(10.0, 0.0, 0.0, 6.0))
    await asyncio.sleep(60)

    # Drones retornam ao ponto de decolagem
    print("-- Returning to the launch point")
    await drone1.action.return_to_launch()
    await drone2.action.return_to_launch()
    await drone3.action.return_to_launch()

    try:
        print("Drone 1 returning to launch")
        await drone1.action.return_to_launch()
    except:
        try:
            await drone1.action.land()
        except:
            print("Drone 1 could not neither return to launch or land")

    try:
        # print("Drone 2 returning to launch")
        await drone2.action.return_to_launch()
    except:
        try:
            await drone2.action.land()
        except:
            print("Drone 2 could not neither return to launch or land")

    try:
        print("Drone 3 returning to launch")
        await drone3.action.return_to_launch()
    except:
        try:
            await drone3.action.land()
        except:
            print("Drone 3 could not neither return to launch or land")


async def camera1():
    while True:
        # print(f"Taking photos Drone1. . .")
        client = airsim.MultirotorClient()

        raw_image = client.simGetImage("0", airsim.ImageType.Scene, vehicle_name='Drone1')
        # print('Retrieved images: %d' % len(rawImage))

        png = cv2.imdecode(airsim.string_to_uint8_array(raw_image), cv2.IMREAD_UNCHANGED)
        cv2.imshow("Depth", png)
        # Delay to take photos
        await asyncio.sleep(2)


async def camera2():
    while True:
        # print(f"Taking photos Drone2. . .")
        client = airsim.MultirotorClient()

        raw_image = client.simGetImage("0", airsim.ImageType.Scene, vehicle_name='Drone2')
        # print('Retrieved images: %d' % len(raw_image))

        png = cv2.imdecode(airsim.string_to_uint8_array(raw_image), cv2.IMREAD_UNCHANGED)
        cv2.imshow("Depth", png)
        # Delay to take photos
        await asyncio.sleep(2)


async def camera3():
    while True:
        # print(f"Taking photos Drone3. . .")
        client = airsim.MultirotorClient()

        raw_image = client.simGetImage("0", airsim.ImageType.Scene, vehicle_name='Drone3')
        # print('Retrieved images: %d' % len(raw_image))

        png = cv2.imdecode(airsim.string_to_uint8_array(raw_image), cv2.IMREAD_UNCHANGED)
        cv2.imshow("Depth", png)
        # Delay to take photos
        await asyncio.sleep(2)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())

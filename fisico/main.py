#!/usr/bin/env python3

import asyncio
from mavsdk import System
from mavsdk.offboard import (VelocityBodyYawspeed, OffboardError)


async def print_position(drone): # Define a função para pegar a posição do drone
    async for position in drone.telemetry.position():
        print(position)
        break


async def run():

    drone = System()
    await drone.connect(system_address="udp://:14540")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"Drone discovered!")
            break

    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok:
            print("Global position estimate ok")
            break

    print("-- Arming")
    await drone.action.arm()

    await drone.action.set_takeoff_altitude(10)  # Configura a altitude de decolagem para 10 m
    print("-- Taking off")
    await drone.action.takeoff()
    await asyncio.sleep(20)

    print("-- Printing position")
    await print_position(drone)

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

    print("-- Going forward at 3 m/s")
    await drone.offboard.set_velocity_body(
        VelocityBodyYawspeed(3.0, 0.0, 0.0, 0.0))

    while True:   # "Pausa" no código até que o fogo seja detectadoos
        # Roda o código de detecção e retorna se tem fogo
        tem_fogo = True
        await asyncio.sleep(15)
        if tem_fogo:
            break

    print("-- Stopping offboard")
    try:
        await drone.offboard.stop()
    except OffboardError as error:
        print(f"Stopping offboard mode failed with error code: \
                  {error._result.result}")

    print("-- Printing position")
    await print_position(drone)

    print("-- Returning to launch and landing")
    await drone.action.return_to_launch()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())

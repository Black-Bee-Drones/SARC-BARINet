import asyncio

from mavsdk import System
from mavsdk.offboard import (OffboardError, VelocityBodyYawspeed)


async def run():
    """ Does Offboard control using velocity body coordinates. """

    drone = System()
    await drone.connect(system_address="udp://:14540")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"Drone discovered!")
            break

    print("-- Arming")
    await drone.action.arm()

    print("-- Setting initial setpoint")
    await drone.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))

    print("-- Starting offboard")
    try:
        await drone.offboard.start()
    except OffboardError as error:
        print(f"Starting offboard mode failed with error code: \
              {error._result.result}")
        print("-- Disarming")
        await drone.action.disarm()
        return

    print("-- Taking off")
    await drone.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, -5.0, 0.0))
    await asyncio.sleep(8)

    print("-- Wait for a bit")
    await drone.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
    await asyncio.sleep(2)

    #Drones rotacionam em direção aos pontos de início
    print("-- Rotating")
    await drone.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, 0.0, -30.0))
    await asyncio.sleep(3)

    print("-- Wait for a bit")
    await drone.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
    await asyncio.sleep(2)

    #Drones das extremidades se distanciam do central
    print("-- Going to the first waypoint")
    await drone.offboard.set_velocity_body(
        VelocityBodyYawspeed(10.0, 0.0, 0.0, 0.0))
    await asyncio.sleep(25)

    print("-- Wait for a bit")
    await drone.offboard.set_velocity_body(
        VelocityBodyYawspeed(0.0, 0.0, 0.0, 30.0))
    await asyncio.sleep(3)
    
    print("-- Starting patrol")
    await drone.offboard.set_velocity_body(
        VelocityBodyYawspeed(3.0, 0.0, 0.0, 6.0))
    await asyncio.sleep(60)

    print("-- Going to the second waypoint")
    await drone.offboard.set_velocity_body(
        VelocityBodyYawspeed(10.0, 0.0, 0.0, 0.0))
    await asyncio.sleep(18)

    print("-- Returning to the launch position")
    await drone.action.return_to_launch()

    print("-- Stopping offboard")
    try:
        await drone.offboard.stop()
    except OffboardError as error:
        print(f"Stopping offboard mode failed with error code: \
              {error._result.result}")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
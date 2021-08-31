
import asyncio
from mavsdk import System
from mavsdk import telemetry


async def run():

    drone1 = System(mavsdk_server_address="localhost", port=50040)
    drone2 = System(mavsdk_server_address="localhost", port=50041)
    drone3 = System(mavsdk_server_address="localhost", port=50042)

    await drone1.connect(system_address="udp://:14540")
    await drone2.connect(system_address="udp://:14541")
    await drone3.connect(system_address="udp://:14542")

    print(f"{drone1.telemetry.health}, {drone2.telemetry.health}, {drone3.telemetry.health}"
    
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

    print("-- Arming")
    await drone1.action.arm()

    print("-- Arming 2 ")
    await drone2.action.arm()

    print("-- Arming 3 ")
    await drone3.action.arm()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())

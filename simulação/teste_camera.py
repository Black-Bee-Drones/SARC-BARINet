import asyncio

from asyncio.events import get_event_loop
from asyncio.tasks import ensure_future
from fire_simulation import drone
    

async def main():
    drone_fly = asyncio.ensure_future(drone1(camera1()))
    tirando_foto = asyncio.ensure_future(camera1())

    await drone_fly
    await tirando_foto


async def drone1():
    print("Waiting to mavsdk to be ready")
    await asyncio.sleep(1)

    print("Waiting Drone 1 to connect")
    await asyncio.sleep(1)


    print("Drone 1 discovered!")
    await asyncio.sleep(1)

    print("-- Arming")
    await asyncio.sleep(0.5)
    print("-- Taking off")

    print("Climbing to 50m above")
    await asyncio.sleep(15)

    print("Returning to launch")
    await asyncio.sleep(5)

    print('Landing')


async def camera1():
    for i in range(20):
        print(f'taking photos {i}')
        if i == 10:
            print('Tem fogo')
            break

        await asyncio.sleep(1)
    return True


if __name__ == '__main__':
    loop = get_event_loop()
    loop.run_until_complete(main())



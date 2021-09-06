'''
[ x ] Definir a home

[ x ] Decolar e ir para o ponto de início

[   ] Detectar fogo (ajuda da galera da detecção)

[ x ] Cameras tirando fotos

[   ] Movimentar o drone em uma área pré-definida

[   ] Comunicação entre os drones (para quando encontrar fogo)

[  ] Enviar as coordenadas um para o outro quando fogo for encontrado

[   ] Análise em raio de 10 metros

[   ] Função de coordenada inicial recebe as novas coordenadas e o processo é repetido

[   ] Retorno ao ponto de home
'''


import airsim
import cv2
import asyncio
from mavsdk import System, action
from mavsdk.mission import (MissionItem, MissionPlan)


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

    #Drones armam
    print("-- Arming")
    await drone1.action.arm()

    print("-- Arming 2 ")
    await drone2.action.arm()

    print("-- Arming 3 ")
    await drone3.action.arm()

    #Drones decolam 
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

    #Drones vão para o ponto de início
    print("-- Going to the seted point")
    await drone1.action.goto_location(-22.41045229156762, -45.451661754067395, 850, 0) 
    print("-- Going to the seted point 2")
    await drone2.action.goto_location(-22.41371539301897, -45.44558583950819, 850, 0)
    print("-- Going to the seted point 3")
    await drone3.action.goto_location(-22.413776005704467, -45.45026259433155, 850, 0)

    #Primeiro varrimento em linha reta(Falta adicionar as coordenadas)
    print("-- Going to the first waypoint")
    await drone1.action.goto_location( -22.41045229156742, -45.451661754067415, 850, 0)
    print("-- Going to the first waypoint 2")
    await drone2.action.goto_location( lat, long, alt, yaw)
    print("-- Going to the first waypoint 3")
    await drone3.action.goto_location( lat, long, alt, yaw)

    #Segundo varrimento em linha reta(Falta adicionar as coordenadas)
    print("-- Going to the second waypoint")
    await drone1.action.goto_location( lat, long, alt, yaw)
    print("-- Going to the second waypoint 2")
    await drone2.action.goto_location( lat, long, alt, yaw)
    print("-- Going to the second waypoint 3")
    await drone3.action.goto_location( lat, long, alt, yaw)
    #Terceiro varrimento em linha reta(caso necessário)
    
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

        rawImage = client.simGetImage("0", airsim.ImageType.Scene, vehicle_name='Drone1')
        # print('Retrieved images: %d' % len(rawImage))

        png = cv2.imdecode(airsim.string_to_uint8_array(rawImage), cv2.IMREAD_UNCHANGED)
        cv2.imshow("Depth", png)
        # Delay to take photos
        await asyncio.sleep(2)


async def camera2():
    while True:
        # print(f"Taking photos Drone2. . .")
        client = airsim.MultirotorClient()

        rawImage = client.simGetImage("0", airsim.ImageType.Scene, vehicle_name='Drone2')
        # print('Retrieved images: %d' % len(rawImage))

        png = cv2.imdecode(airsim.string_to_uint8_array(rawImage), cv2.IMREAD_UNCHANGED)
        cv2.imshow("Depth", png)
        # Delay to take photos
        await asyncio.sleep(2)


async def camera3():
    while True:
        # print(f"Taking photos Drone3. . .")
        client = airsim.MultirotorClient()

        rawImage = client.simGetImage("0", airsim.ImageType.Scene, vehicle_name='Drone3')
        # print('Retrieved images: %d' % len(rawImage))

        png = cv2.imdecode(airsim.string_to_uint8_array(rawImage), cv2.IMREAD_UNCHANGED)
        cv2.imshow("Depth", png)
        # Delay to take photos
        await asyncio.sleep(2)
        
    
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())

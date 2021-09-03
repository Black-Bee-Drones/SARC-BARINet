'''
[ x ] Definir a home

[ x ] Decolar e ir para o ponto de início

[   ] Detectar fogo (ajuda da galera da detecção)

[   ] Movimentar o drone em uma área pré-definida

[   ] Comunicação entre os drones (para quando encontrar fogo)

[  ] Enviar as coordenadas um para o outro quando fogo for encontrado

[   ] Análise em raio de 10 metros

[   ] Função de coordenada inicial recebe as novas coordenadas e o processo é repetido

[   ] Bateria em nível baixo mandando o drone pra casa

    [   ] Retorno ao ponto de home
'''



import asyncio
from mavsdk import System, action


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

    #Drones vão para o ponto de início
    print("-- Going to the seted point")
    await drone1.action.goto_location(-22.41045229156762, -45.451661754067395, 850, 0) 
    print("-- Going to the seted point 2")
    await drone2.action.goto_location(-22.41371539301897, -45.44558583950819, 850, 0)
    print("-- Going to the seted point 3")
    await drone3.action.goto_location(-22.413776005704467, -45.45026259433155, 850, 0)

    
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())

#!/usr/bin/env python3
import asyncio
from asyncio.events import get_event_loop
from mavsdk import System
from mavsdk.offboard import (OffboardError, VelocityBodyYawspeed,VelocityNedYaw, PositionNedYaw)

#Definição do drone 1 como variável global para poder utilizar em qualquer função assíncrona
drone2 = System(mavsdk_server_address='localhost', port=50041)


async def main():
    
    drone_voando = asyncio.create_task(movimentacao_drone2())
    await drone_voando


async def movimentacao_drone2():
    
    global drone2
    
    #Drone se conecta
    await drone2.connect(system_address="udp://:14540")
    
    print("Waiting for drone 2 to connect...")
    async for state in drone2.core.connection_state():
        if state.is_connected:
            print(f"Drone 2 discovered!")
            break

    # Setando valores iniciais para o offboard
    print("-- Setting initial setpoint")
    await drone2.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))

    await drone2.offboard.set_velocity_ned(VelocityNedYaw(0, 0, 0, 0))
    
    await drone2.offboard.set_position_ned(PositionNedYaw(0, 0, 0, 0))

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
    await drone2.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0,-6.0, 7))
    await asyncio.sleep(15)
    
    await drone2.offboard.set_velocity_body(VelocityBodyYawspeed(0, 0, 0, 0))
    await asyncio.sleep(5)

    print("da uma giradinha e vai pra tras")

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
    await drone2.offboard.set_velocity_body(VelocityBodyYawspeed(4, 0, 0 ,0))
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
    drone2_fly = asyncio.create_task(movimentacao_drone2())
    await drone2_fly
    """
    i = 0
    while True:
        # print(f"Foto {i}")
        i += 1
        await asyncio.sleep(1)
    """ 

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
#!/usr/bin/env python3
import asyncio
from asyncio.events import get_event_loop
from mavsdk import System
from mavsdk.offboard import (OffboardError, VelocityBodyYawspeed,VelocityNedYaw, PositionNedYaw)
# import airsim
# import numpy as np
# import os
# import tempfile
# import cv2


#Definição do drone 1 como variável global para poder utilizar em qualquer função assíncrona

drone3 = System(mavsdk_server_address='localhost', port=50042)

async def main():
    
    drone_voando = asyncio.create_task(movimentacao_drone3())
    await drone_voando


async def movimentacao_drone3():
    
    global drone3
    
    #Drone se conecta
    await drone3.connect(system_address="udp://:14540")
    
    print("Waiting for drone 1 to connect...")
    async for state in drone3.core.connection_state():
        if state.is_connected:
            print(f"Drone 1 discovered!")
            break

    # Setando valores iniciais para o offboard
    print("-- Setting initial setpoint")
    await drone3.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))

    await drone3.offboard.set_velocity_ned(VelocityNedYaw(0, 0, 0, 0))
    
    await drone3.offboard.set_position_ned(PositionNedYaw(0, 0, 0, 0))

    # Iniciando o Offboard
    try:
        await drone3.offboard.start()
    except OffboardError as error:
        print(f"Start Drone 1 offboard failed with error code: {error._result.result}")
        print("-- Drone 1  Disarming")
        await drone3.action.disarm()
        return

    # Drone arma
    print("-- Arming")
    await drone3.action.arm()
    
    print("-- Takeoff")
    await drone3.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0,-5.0, -14))
    await asyncio.sleep(15)
    
    print("Indo pra frente. . .")
    await drone3.offboard.set_velocity_body(VelocityBodyYawspeed(5, 0, 0, 0))
    await asyncio.sleep(43)

    print('Subindo. . .')
    await drone3.offboard.set_velocity_body(VelocityBodyYawspeed(0, 0, -4, 0))
    await asyncio.sleep(10)

    print("Dando uma giradinha")
    await drone3.offboard.set_velocity_body(VelocityBodyYawspeed(0, 0, 0, -27,))
    await asyncio.sleep(20)

    print("Voltando para o ponto inicial")
    await drone3.offboard.set_position_ned(PositionNedYaw(0, 0, -60, 0))
    await asyncio.sleep(25)
    
    # Para o offboard
    print("-- Stopping offboard")
    try:
        await drone3.offboard.stop()
    except OffboardError as error:
        print(f"Stopping offboard mode failed with error code: \
              {error._result.result}")

    
    await drone3.action.return_to_launch()
    await asyncio.sleep(20)
    

async def camera3():
    drone3_fly = asyncio.create_task(movimentacao_drone3())
    await drone3
    

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
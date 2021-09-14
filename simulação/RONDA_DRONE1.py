#!/usr/bin/env python3
import asyncio
from asyncio.events import get_event_loop
from mavsdk import System
from mavsdk.offboard import (OffboardError, VelocityBodyYawspeed,VelocityNedYaw, PositionNedYaw,Attitude)

#Definição do drone 1 como variável global para poder utilizar em qualquer função assíncrona
drone1 = System(mavsdk_server_address='localhost', port=50040)

async def main():
    
    drone_voando = asyncio.create_task(movimentacao_drone1())
    await drone_voando


async def movimentacao_drone1():
    
    global drone1
    
    #Drone se conecta
    await drone1.connect(system_address="udp://:14540")
    
    print("Waiting for drone 1 to connect...")
    async for state in drone1.core.connection_state():
        if state.is_connected:
            print(f"Drone 1 discovered!")
            break

    # Setando valores iniciais para o aoffboard
    print("-- Setting initial setpoint")
    await drone1.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))

    await drone1.offboard.set_velocity_ned(VelocityNedYaw(0, 0, 0, 0))
    
    await drone1.offboard.set_position_ned(PositionNedYaw(0, 0, 0, 0))

    await drone1.offboard.set_attitude(Attitude(0.0, 0.0, 0.0, 0.0))

    # Iniciando o Offboard
    try:
        await drone1.offboard.start()
    except OffboardError as error:
        print(f"Start Drone 1 offboard failed with error code: {error._result.result}")
        print("-- Drone 1  Disarming")
        await drone1.action.disarm()
        return

    # Drone arma
    print("-- Arming")
    await drone1.action.arm()
   
    print("-- Takeoff")
    await drone1.offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0,-6.0, -7))
    await asyncio.sleep(15)
    

    print("da uma giradinha e vai pra tras")
    await drone1.offboard.set_velocity_body(VelocityBodyYawspeed(4, 0, 0, 0))
    await asyncio.sleep(15)

    print("Primeira curva")
    await drone1.offboard.set_velocity_body(VelocityBodyYawspeed(7, 0, -1, 28))
    await asyncio.sleep(6)
    await drone1.offboard.set_velocity_body(VelocityBodyYawspeed(4, 0, 0, 0))
    await asyncio.sleep(22)

    print("Segunda curva")
    await drone1.offboard.set_velocity_body(VelocityBodyYawspeed(7, 0, -1, -28))
    await asyncio.sleep(6)
    await drone1.offboard.set_velocity_body(VelocityBodyYawspeed(4,0,0,0))
    await asyncio.sleep(30)

    print("Terceira curva")
    await drone1.offboard.set_velocity_body(VelocityBodyYawspeed(7, 0, -1, 28))
    await asyncio.sleep(6)
    await drone1.offboard.set_velocity_body(VelocityBodyYawspeed(4, 0, 0 ,0))
    await asyncio.sleep(18)
    
    print("Quarta Curva") 
    await drone1.offboard.set_velocity_body(VelocityBodyYawspeed(7, 0, -1,-28))
    await asyncio.sleep(6)
    
    print("Subindo 70m")
    await drone1.offboard.set_velocity_body(VelocityBodyYawspeed(0, 0, -5, 0))
    await asyncio.sleep(14)

    print("Girando")
    await drone1.offboard.set_velocity_body(VelocityBodyYawspeed(0, 0, 0, 63))
    await asyncio.sleep(3)
    
    print("PARA PARA PARA PARA PARA")
    await drone1.offboard.set_velocity_body(VelocityBodyYawspeed(0, 0, 0, 0))
    await asyncio.sleep(5)
    
    print("Girando de volta")
    await drone1.offboard.set_velocity_body(VelocityBodyYawspeed(0, 0, 0, -63))
    await asyncio.sleep(3)
    
    print("Indo pra frente")
    await drone1.offboard.set_velocity_body(VelocityBodyYawspeed(4, 0, 0, 00))
    await asyncio.sleep(15)

    print("voltando pro inicio")
    await drone1.offboard.set_position_ned(PositionNedYaw(0, 0, -40, 140))
    await asyncio.sleep(20)

    # Para o offboard
    print("-- Stopping offboard")
    try:
        await drone1.offboard.stop()
    except OffboardError as error:
        print(f"Stopping offboard mode failed with error code: \
              {error._result.result}")

    
    await drone1.action.return_to_launch()
    await asyncio.sleep(15)
    

async def camera1():
    drone1_fly = asyncio.create_task(movimentacao_drone1())
    await drone1_fly
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

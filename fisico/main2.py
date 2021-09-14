#!/usr/bin/env python3
import asyncio
from asyncio.events import get_event_loop
from mavsdk import System
from mavsdk.offboard import (OffboardError, VelocityBodyYawspeed)
import cv2
import time
import detection

# Definição do drone 1 como variável global para poder utilizar em qualquer função assíncrona
drone = System()

async def main():
    
    #Nesse programa a função de movimentação é dependente da função da camera e no momento que "encontrar fogo" a task de movimenaçao é cancelada

    cam = asyncio.create_task(camera())
    await cam

    #New trajeto é a função de "o que ele vai fazer depois de encontrar fogo?"
    #Sim senhor!
    
    # new_trajeto = asyncio.create_task(novo_trajeto())
    # await new_trajeto


async def movimentacao_drone():
    global drone
    
    #Drone se conecta
    await drone.connect(system_address="serial://COM3:57600")
    
    print("Waiting for drone 1 to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"Drone discovered!")
            break

    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok:
            print("Global position estimate ok")
            break
    
    await drone.action.set_takeoff_altitude(3)  # Configura a altitude de decolagem para 3 m
    print("-- Taking off")
    await drone.action.takeoff()
    await asyncio.sleep(12)

    # Setando valores iniciais para offboard
    
    await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0, 0, 0, 0))
  
    # Iniciando o Offboard
    try:
        await drone.offboard.start()
    except OffboardError as error:
        print(f"Start Drone 1 offboard failed with error code: {error._result.result}")
        print("-- Drone 1  Disarming")
        await drone.action.disarm()
        return

        #Gira 360 graus
    print('Girando. . .')
    await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0, 0, 0, 45))
    await asyncio.sleep(16)

    #Para o offboard
    print("-- Stopping offboard")
    try:
        await drone.offboard.stop()
    except OffboardError as error:
        print(f"Stopping offboard mode failed with error code: \
              {error._result.result}")

    #Pousa o drone
    print("-- Landing")
    await drone.action.land()
    await asyncio.sleep(10)

    #Desarma o drone
    print("Desarming. . .")
    await drone.action.disarm()

#Função da camera
async def camera():
    drone_fly = asyncio.create_task(movimentacao_drone())
    
    precision = 0.75
    
    cap = cv2.VideoCapture(0)

    if (cap.isOpened() == False): 
        print("Error opening video stream or file")

    while(cap.isOpened()):
        ret, frame = cap.read()

        if ret == True:
            start = time.time()
            results = detection.detect(frame, precision)

            if results is not None:
                print(results)
                cv2.rectangle(frame, (results[0][0], results[0][1]), (results[1][0], results[1][1]), (125, 255, 51), thickness=2)
                cv2.putText(frame, "{:.2f}".format(results[2]), (results[0][0], results[0][1]), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,0,0), 2)

            end = time.time()
            fps = 1 / (end-start)
            print("FPS: ", "{:.2f}".format(fps))

            cv2.imshow('Janela', frame)

            # Press Q on keyboard to  exit
            await asyncio.sleep(0.1)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Achei fogo")
                asyncio.Task.cancel(drone_fly)
                break

        else: 
            break

    cap.release()
    cv2.destroyAllWindows()

#Trajeto que será feito após a detecção de fogo
async def novo_trajeto():
    global drone

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"Drone discovered!")
            break
    
    #Gira 360 graus para o lado oposto
    await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0, 0, 0, -45))
    await asyncio.sleep(8)
    
    #Pousa o drone
    print("-- Landing")
    await drone.action.land()
    await asyncio.sleep(8)

    #Desarma o drone
    print("Desarming. . .")
    await drone.action.disarm()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

# SARC-BARINet

Projetos do código para o drone físico e simulação via AirSim da competição da SARC-BARINet, com o tema: detecção de focos de incêndio. Uso de visão computacional para processamento de imagens e da API Mavsdk para controle do drone.

# Drone Físico

O drone físico tem um código relativamente simples. O drone decola, voa para frente (relativa à posição de launch), espera detectar fogo e quando detecta, retorna imagens de satélite, para logo após voltar para o ponto de launch.

Para o deploy do código do drone físico, é importante lembrar de algumas coisas. De ínício, verifique se a versão do Python está igual ou acima da 3.6.

Depois, faça as instalações que seguem.
```sh
pip install mavsdk
```
```sh
pip install mercantile
```
```sh
pip install pillow
```
Observações:
- Talvez você precise mudar pip por pip3.
- As duas últimas instalações são para o processamento das imagens de satélite.

E com isso, o código pode ser rodado sem problemas.

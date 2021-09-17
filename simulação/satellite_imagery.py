import shutil
import mercantile
import requests
import math
from PIL import Image
from PIL import ImageDraw
from os import listdir
from pathlib import Path

# lugar aleatório -11.363034, -42.966699
# unifei          -22.412797, -45.449770
# sao mateus      -18.715110, -39.875167
# casa do rodrigo -22.42072, -45.44611

# definições gerais


def get_satellite_image(vetor_latitude_longitude):
    z = 15  # zoom

    # definições para a imagem composta
    delta = 0.0055
    bottom_right = [vetor_latitude_longitude[0] - delta, vetor_latitude_longitude[1] + delta]
    top_left = [vetor_latitude_longitude[0] + delta, vetor_latitude_longitude[1] - delta]
    tile_bottom_right = mercantile.tile(bottom_right[1], bottom_right[0], z)
    tile_top_left = mercantile.tile(top_left[1], top_left[0], z)
    x_tile_range = (tile_top_left[0], tile_bottom_right[0])
    y_tile_range = (tile_top_left[1], tile_bottom_right[1])

    # cria repositórios
    Path("./composite_images/").mkdir(parents=True, exist_ok=True)
    Path("./elevation_images/").mkdir(parents=True, exist_ok=True)

    # puxa a imagem de satélite
    r = requests.get(
        'https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/'
        + str(vetor_latitude_longitude[1]) + ',' + str(vetor_latitude_longitude[0]) + ',16,0' +
        '/300x200@2x?access_token=pk.eyJ1IjoiZGllbHNvIiwiYSI6ImNrdDAzdmwwNTAxazQydm1oOWg3ajZ2d3gifQ.' +
        'Y-miIzp9s7r0U59NhLVAbQ',
        stream=True)
    # salva a imagem de satélite
    with open('./composite_images/' + 'satellite_img @ ' + str(vetor_latitude_longitude) + '.jpeg', 'wb') as f:
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)

    # puxa a imagem de relevo
    for i, x in enumerate(x_tile_range):
        for j, y in enumerate(y_tile_range):  # Call the URL to get the image back
            r = requests.get('https://api.mapbox.com/v4/mapbox.terrain-rgb/' + str(z) + '/' + str(x) + '/' + str(y) +
                             '@2x.pngraw?access_token=pk.eyJ1IjoiZGllbHNvIiwiYSI6ImNrdDAzdmwwNTAxaz' +
                             'Qydm1oOWg3ajZ2d3gifQ.Y-miIzp9s7r0U59NhLVAbQ',
                             stream=True)  # Next we will write the raw content to an image
            with open('./elevation_images/' + str(i) + '.' + str(j) + '.png', 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

    # lista as imgs
    image_files = ['./elevation_images/' +
                   f for f in listdir('./elevation_images/')]

    # abre as imagens
    images = [Image.open(x) for x in image_files]

    # define a qtd de tiles
    edge_length_y = 2
    edge_length_x = 2

    # Find the final composed image dimensions
    width, height = images[0].size
    total_width = width * edge_length_x
    total_height = height * edge_length_y

    # Create a new blank image we will fill in
    composite = Image.new('RGB', (total_width, total_height))

    # Loop over the x and y ranges
    y_offset = 0
    for i in range(0, edge_length_x):
        x_offset = 0
        for j in range(0, edge_length_y):
            # Open up the image file and paste it into the composed image at the given offset position
            tmp_img = Image.open('./elevation_images/' + str(i) + '.' + str(j) + '.png')
            composite.paste(tmp_img, (y_offset, x_offset))
            x_offset += width  # Update the width

        y_offset += height  # Update the height

    # Save the final image
    composite.save('./composite_images/elevation_image.png')

    with Image.open('./composite_images/satellite_img @ ' + str(vetor_latitude_longitude) + '.jpeg') as im:
        draw = ImageDraw.Draw(im)
        draw.ellipse([250, 150, 350, 250], outline=(255, 0, 0), width=2)

    # puxa a latitude e a longitude do tile de cima esquerda
    lng_lat_top_left = mercantile.ul(tile_top_left)
    lng_lat_bottom_right = mercantile.ul(tile_bottom_right)

    # calcula a razão pixel/grau horizontal e vertical
    pixel_degree_ratio_horizontal = 512 / (lng_lat_top_left[1] - lng_lat_bottom_right[1])

    pixel_degree_ratio_vertical = 512 / (lng_lat_bottom_right[0] - lng_lat_top_left[0])

    # calcula a distancia, em graus, do tile cima esquerda até a coordenada de destino
    horizontal_distance_degrees = vetor_latitude_longitude[1] - lng_lat_top_left[0]
    print(horizontal_distance_degrees)

    vertical_distance_degrees = lng_lat_top_left[1] - vetor_latitude_longitude[0]
    print(vertical_distance_degrees)
    # transforma (roughly) a distancia de graus para pixels
    horizontal_distance_pixels = (int(horizontal_distance_degrees * pixel_degree_ratio_horizontal -
                                      (60 * lng_lat_top_left[1] / lng_lat_bottom_right[1]) *
                                      (math.sin(horizontal_distance_degrees *
                                                360 * math.pi /
                                                ((lng_lat_top_left[1] - lng_lat_bottom_right[1]) * 180)))))
    vertical_distance_pixels = (int((vertical_distance_degrees * pixel_degree_ratio_vertical) -
                                    (60 * lng_lat_top_left[0] / lng_lat_bottom_right[0]) *
                                    (math.sin(vertical_distance_degrees / 10 *
                                              360 * math.pi /
                                              ((lng_lat_top_left[0] - lng_lat_bottom_right[0]) * 180)))))

    print(horizontal_distance_pixels)
    print(vertical_distance_pixels)

    # desenha um círculo na coordenada dada
    with Image.open('./composite_images/elevation_image.png') as secim:
        draw = ImageDraw.Draw(secim)
        draw.ellipse([horizontal_distance_pixels - 40, vertical_distance_pixels - 40,
                      horizontal_distance_pixels + 40, vertical_distance_pixels + 40], outline=(255, 0, 0), width=3)
        secim.show()
        im.show()  # exibe as imagens

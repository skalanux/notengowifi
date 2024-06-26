import os
import sys
import cv2
import numpy as np
import time
from morse_equivs import equivs
import argparse
import time
from pprint import pprint
from collections import defaultdict

parser = argparse.ArgumentParser(
    prog='NoTengoWifi',
    description='transcript morse code that was send to this computer by webcam',
    epilog='Gracias')

parser.add_argument("-c", "--control", action="store_true")
args = parser.parse_args()
if args.control:
    print("Modo control")
    for i in range(1,6):
        time.sleep(1)
        print(".", end="", flush=True)

def is_light_on(frame, threshold=250, min_brightness_area=33500):
    # Convertir el frame a escala de grises
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Aplicar un umbral para detectar las áreas brillantes
    _, thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)

    # Encontrar los contornos de las áreas brillantes
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Calcular el área total de las regiones brillantes
    bright_area = sum(cv2.contourArea(contour) for contour in contours)

    # Determinar si la luz está encendida o apagada
    light_on = bright_area > min_brightness_area

    return light_on, bright_area, thresh

# Capturar el video desde la cámara
cap = cv2.VideoCapture(0)  # Cambiar el índice si hay más de una cámara

last_checked_time = time.time()
check_interval =  0.01 # Intervalo de tiempo para verificar el estado de la luz en segundos

cant_lights = 0
cant_darks = 0
symbols = ''

palabra = ''
times_list = []
last_value = False
light_dark_count = 0

INTERVAL_BETWEEN_WORDS = (13,20) # OK
INTERVAL_BETWEEN_SYMBOLS = (3,12)
LIGHT_INTERVAL_DOT = (1,7)
LIGHT_INTERVAL_DASH = (8,20)

STRING_CONTROL = "- . -_._._- - -_-_-/-_._. ./-_._-_. -_-_- -_. - ._-_. -_-_- ._-_._." # "texto de control"

def print2(value):
    global palabra
    palabra+=value
    print(value)


def write_to_fifo(char):
    with open('myfifo', 'w') as fifo:
        if char is not None:
            fifo.write(char)
            fifo.flush()  # Asegúrate de que los datos se escriban inmediatamente
def new_config (string_control, time_list):
    maximo = max(time_list)
    tipos_tiempo = defaultdict(list)


    for indice, tiempo in enumerate(time_list):
        tipos_tiempo[string_control[indice]].append(tiempo)
    return tipos_tiempo


print_space = False
print_symbol = False
keep_scanning = True

time.sleep(2)
print("Decoding...")

while keep_scanning:
    ret, frame = cap.read()
    if not ret:
        break

    light_on, bright_area, thresh = is_light_on(frame)


    print_space = False
    print_symbol = False

    if light_on != last_value:
        if ((len(times_list) == 0 and light_on) or len(times_list) != 0) and light_dark_count !=0:
            if light_on:
                estado = "luz"
            else:
                estado = "oscuridad"
            print("Agregando valor de ", estado, " a la lista: ", light_dark_count)
            times_list.append(light_dark_count)
            light_dark_count = 0
    else:
        light_dark_count+=1
    last_value = light_on
    if light_dark_count == 50:
        print(times_list)
        print ("longitud de string de control: ", len(STRING_CONTROL))
        print ("longitud de lista de control obtenida: ", len(times_list))
        print(new_config(STRING_CONTROL, times_list))

        exit()


    if light_on:
        cant_lights+=1
        if cant_darks>0:
            if cant_darks in range(*INTERVAL_BETWEEN_WORDS):
                print_space = True
                print_symbol = True
            elif cant_darks in range(*INTERVAL_BETWEEN_SYMBOLS):
                print_symbol = True

        cant_darks=0
    else:
        cant_darks+=1
        if cant_lights>0:
            if cant_lights in range(*LIGHT_INTERVAL_DOT):
                symbols+='.'
            elif cant_lights in range(*LIGHT_INTERVAL_DASH):
                symbols+='-'

        cant_lights=0

        if cant_darks > INTERVAL_BETWEEN_WORDS[1] and symbols:
            print_symbol = True
            #keep_scanning = False

    if print_symbol and not args.control:
        #print(symbols, equivs.get(symbols))
        #print(equivs.get(symbols))
        letter=equivs.get(symbols)
        #sys.stdout.write(letter)
        write_to_fifo(letter)
        symbols=''
    if print_space and not args.control:
        #print(" \\ ")
        #print(" ")
        #sys.stdout.write(' ')
        write_to_fifo(' ')
        symbols=''
    #sys.stdout.flush()
    # Mostrar el frame original y el frame con el umbral aplicado
    #cv2.imshow("Frame", frame)
    #cv2.imshow("Threshold", thresh)

    # Salir del loop si se presiona la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar el objeto de captura y cerrar todas las ventanas
cap.release()
cv2.destroyAllWindows()


import cv2
import numpy as np
import time

def is_light_on(frame, threshold=250, min_brightness_area=23500):
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
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    current_time = time.time()
    if current_time - last_checked_time >= check_interval:
        light_on, bright_area, thresh = is_light_on(frame)
        last_checked_time = current_time
        
        # Mostrar el estado de la luz
        if light_on:
            cant_lights+=1
            if cant_darks>0:
                if cant_darks>=5:
                    sym = '/'
                    print(f" {sym}", end='')
                cant_darks=0
        else:
            cant_darks+=1
            if cant_lights>0:
                if cant_lights>10:
                    sym = '_'
                else:
                    sym = '.'
                print(f" {sym}", end='')
            cant_lights=0
    
    # Mostrar el frame original y el frame con el umbral aplicado
        cv2.imshow("Frame", frame)
        cv2.imshow("Threshold", thresh)
        
    # Salir del loop si se presiona la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar el objeto de captura y cerrar todas las ventanas
cap.release()
cv2.destroyAllWindows()

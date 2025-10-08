import math
import cv2 as cv
import numpy as np
import random as ran

img_width, img_height = 800, 800
x_c, y_c = img_width // 2, img_height // 2

img1 = np.zeros((img_height, img_width, 3), np.uint8)
img2 = np.zeros((img_height, img_width, 3), np.uint8)
img3 = np.zeros((img_height, img_width, 3), np.uint8)

a = 170 # escala de la figura
theta = 0 #angulo de rotacion

#variables para control del hipocicloide
n_puntas = 10
R = a #radio del hipocicloide
r = a / n_puntas #radio del ciclo pequeño

while True:
    # color aleatorio en BGR
    color = (ran.randint(0, 255), ran.randint(0, 255), ran.randint(0, 255))
    
    # radio del cardioide en coordenadas polares
    rCardioide = a * (0.7 - math.cos(theta))

    # transformación polar -> cartesiano
    xCardioide = int(x_c - rCardioide * math.cos(theta))
    yCardioide = int(y_c - rCardioide * math.sin(theta))
    cv.circle(img1, (xCardioide, yCardioide), 3, color, -1)
    
    #hipocicloide
    xHipocicloide = int(x_c + (R - r) * math.cos(theta) + r * math.cos((R - r) / r * theta))
    yHipocicloide = int(y_c + (R - r) * math.sin(theta) - r * math.sin((R - r) / r * theta))
    cv.circle(img2, (xHipocicloide, yHipocicloide), 3, color, -1)
    
    #curva de lissajous
    xLissajous = int(x_c + 150*math.sin(3*theta))
    yLissajous = int(y_c + 150*math.cos(5*(theta)))
    cv.circle(img3, (xLissajous, yLissajous), 3, color, -1)

    theta += 0.008

    # mostrar imagenes
    cv.imshow("Curva de Lissajous", img3)
    cv.imshow(("Hipocilcoide de %d puntas") %n_puntas, img2)
    cv.imshow("Cardioide", img1)
    
    if cv.waitKey(2) & 0xFF == 27:  # ESC para salir
        break

cv.destroyAllWindows()
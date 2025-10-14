#2025-10-13
#Imagen 1:
#escalar factor 2, aplicar filtro
#rotar 45 grados, aplicar filtro
# ----------------------------------------
#Imagen 2:
#escalar factor 2
#rotar 45 grados
#aplicar filtro
# ----------------------------------------
#Imagen 3:
#trasladar al centro
#rotar 90 grados
#escalar factor 2
#aplicar filtro
# ---------------------------------------- 

import cv2 as cv
import numpy as np
import math

img = cv.imread("Imagenes/prueba3.jpg", 0)
x, y = img.shape

def trasladar(imagen, dx, dy):
    alto, ancho = imagen.shape
    imgTrasladada = np.zeros((alto, ancho), dtype=np.uint8)
    
    for i in range(alto):
        for j in range(ancho):
            xTrasladada = i + dx
            yTrasladada = j + dy
            if 0 <= xTrasladada < alto and 0 <= yTrasladada < ancho:
                imgTrasladada[xTrasladada, yTrasladada] = imagen[i, j]
    return imgTrasladada

def escalar(imagen, factorEscalado):
    alto, ancho = imagen.shape
    imgEscalada = np.zeros((alto * factorEscalado, ancho * factorEscalado), dtype=np.uint8)
    
    for i in range(alto):
        for j in range(ancho):
            imgEscalada[i * factorEscalado, j * factorEscalado] = imagen[i, j]
    return imgEscalada

def rotar(imagen, angulo):
    alto, ancho = imagen.shape
    imgRotada = np.zeros((alto, ancho), dtype=np.uint8)
    theta = math.radians(angulo)
    cx, cy = ancho // 2, alto // 2  # Centro de la imagen
    
    for i in range(alto):
        for j in range(ancho):
            new_x = int((j - cx) * math.cos(theta) - (i - cy) * math.sin(theta) + cx)
            new_y = int((j - cx) * math.sin(theta) + (i - cy) * math.cos(theta) + cy)
            if 0 <= new_x < ancho and 0 <= new_y < alto:
                imgRotada[new_y, new_x] = imagen[i, j]
    return imgRotada

def filtroBilineal(imagen):
    alto, ancho = imagen.shape
    #Traajar sobre la copia
    filtro = imagen.copy()

    for i in range(1, alto - 1):
        for j in range(1, ancho - 1):
            
            if filtro[i, j] == 0:
                # Vecinos directos (en cruz)
                arriba = float(filtro[i - 1, j])
                abajo = float(filtro[i + 1, j])
                izquierda = float(filtro[i, j - 1])
                derecha = float(filtro[i, j + 1])
                
                # Vecinos diagonales (en esquinas)
                arribaIzq = float(filtro[i - 1, j - 1])
                arribaDer = float(filtro[i - 1, j + 1])
                abajoIzq = float(filtro[i + 1, j - 1])
                abajoDer = float(filtro[i + 1, j + 1])

                # 
                vecinos_cruz = []
                if arriba > 0: vecinos_cruz.append(arriba)
                if abajo > 0: vecinos_cruz.append(abajo)
                if izquierda > 0: vecinos_cruz.append(izquierda)
                if derecha > 0: vecinos_cruz.append(derecha)
                
                if len(vecinos_cruz) > 0:
                    valor_nuevo = sum(vecinos_cruz) / len(vecinos_cruz)
                    filtro[i, j] = int(valor_nuevo)
                
                else:
                    vecinos_esquina = []
                    if arribaIzq > 0: vecinos_esquina.append(arribaIzq)
                    if arribaDer > 0: vecinos_esquina.append(arribaDer)
                    if abajoIzq > 0: vecinos_esquina.append(abajoIzq)
                    if abajoDer > 0: vecinos_esquina.append(abajoDer)
                    
                    if len(vecinos_esquina) > 0:
                        valor_nuevo = sum(vecinos_esquina) / len(vecinos_esquina)
                        filtro[i, j] = int(valor_nuevo)
    return filtro

escala = 2
#Transformar las imagenes
#Transformaciones para la imagen 1
escalada1 = escalar(img, escala)
fEscalada1 = filtroBilineal(escalada1)
rfEscalada1 = rotar(fEscalada1, 45)
final1 = filtroBilineal(rfEscalada1)
#Transformaciones para la imagen 2
escalada2 = escalar(img, escala)
rotada2 = rotar(escalada2, 45)
final2 = filtroBilineal(rotada2)
#Transformaciones para la imagen 3
trasladada3 = trasladar(img, x//2, y//2)
rotada3 = rotar(trasladada3, 90)
escalada3 = escalar(rotada3, escala)
final3 = filtroBilineal(escalada3)

#Imagen original
cv.imshow("Imagen Original", img)
if cv.waitKey(0) & 0xFF == ord(' '):  # Presiona espacio para salir
    cv.destroyAllWindows()

# Mostrar las transformaciones para la imagen 1
cv.imshow("Escalada 1", escalada1)
cv.imshow("Filtro Escalada 1", fEscalada1)
cv.imshow("Rotada Escalada 1", rfEscalada1)
cv.imshow("Final Imagen 1", final1)
if cv.waitKey(0) & 0xFF == ord(' '):  # Presiona espacio para salir
    cv.destroyAllWindows()
    
print("Resultado de las transformaciones de la imagen 1:")
cv.imshow("Final Imagen 1", final1)
if cv.waitKey(0) & 0xFF == ord(' '):  # Presiona espacio para salir
    cv.destroyAllWindows()

#Mostrar las transformaciones para la imagen 2
cv.imshow("Escalada 2", escalada2)
cv.imshow("Rotada 2", rotada2)
cv.imshow("Final Imagen 2", final2)
if cv.waitKey(0) & 0xFF == ord(' '):  # Presiona espacio para salir
    cv.destroyAllWindows()

print("Resultado de las transformaciones de la imagen 2:")
cv.imshow("Final Imagen 2", final2)
if cv.waitKey(0) & 0xFF == ord(' '):  # Presiona espacio para salir
    cv.destroyAllWindows()

#Transformaciones para la imagen 3
cv.imshow("Trasladada 3", trasladada3)
cv.imshow("Rotada 3", rotada3)
cv.imshow("Escalada 3", escalada3)
if cv.waitKey(0) & 0xFF == ord(' '):  # Presiona espacio para salir
    cv.destroyAllWindows()
    
print("Resultado de las transformaciones de la imagen 3:")
cv.imshow("Final Imagen 3", final3)
print("Presiona ESC para salir")

if cv.waitKey(0) & 0xFF == 27:  # Presiona ESC para salir
    cv.destroyAllWindows()

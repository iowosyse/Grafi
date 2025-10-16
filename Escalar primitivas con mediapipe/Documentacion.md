# Escalado de primitivas utilizando mediapipe   

Primero se importan las librerias necesarias para trabajar con OpenCV y Mediapipe   
```python
import cv2 as cv
import mediapipe as mp
```
Luego se inizializan los objetos con los que se va a trabajar y a partir de los cuales se leerá la información entregada por mediapipe  
```python
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
```
Como es usual, se lee la imágen de la primer cámara que se encuentra, y se muestra cada frame encontrado si es que existe, de lo contrario cierra la cámara.
```python
cap = cv.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break   
```

Se obtienen las dimensiones de la imágen mostrada, primero se retorna el alto, luego el ancho, y al final los canales de color de la imágen

```python
cap = cv.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv.flip(frame, 1)
    h, w, _ = frame.shape
```

Es necesario transformar el modelo BGR de OpenCV a RGB, si no, Mediapipe no mostraría nada en pantalla.
```python
    # Convertir a RGB
    frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

    # Procesar la imagen con MediaPipe
    results = hands.process(frame_rgb)
```
## Mulithandedness - Detección de múltiples manos
Se verifica si Mediapipe lee 2 manos, si sí, se obtiene las coordenadas del índice 8 del arreglo de las manos, que es la punta del dedo índice y se dibujan las landmarks y sus conexiones.
![Distribución de landmarks de la mano](./../Deteccion%20de%20manos%20con%20mediapipe/hand_landmarks.png)
```python
    if results.multi_hand_landmarks and len(results.multi_hand_landmarks) == 2:
        for hand_landmarks in results.multi_hand_landmarks:
            manoIzqLandmarks = results.multi_hand_landmarks[0]
            manoDerLandmarks = results.multi_hand_landmarks[1]
            mp_drawing.draw_landmarks(frame, manoIzqLandmarks, mp_hands.HAND_CONNECTIONS)
            mp_drawing.draw_landmarks(frame, manoDerLandmarks, mp_hands.HAND_CONNECTIONS)
            # Obtener las coordenadas de los dedos índices
            puntaIdxIzq = manoIzqLandmarks.landmark[8]
            puntaIdxDer = manoDerLandmarks.landmark[8]
            
```
En el bloque de código anterior, se puede ver como se extraen ambas manos de la imágen con las líneas
```python
            manoIzqLandmarks = results.multi_hand_landmarks[0]
            manoDerLandmarks = results.multi_hand_landmarks[1]
```
Mediapipe es capaz de soportar múltiples manos en la imágen que lee, y además distinguir si es mano derecha o izquierda. Por defecto, se soporta un máximo de 2 manos, pero puede ser modificado pasandole ese valor como parámetro cuando se invoca el método ```Hands()``` - [Administrador (2024)](https://omes-va.com/mediapipe-hands-python/)  
Se puede obtener más imformación si se aplica la línea 
```python
print('Handedness:', results.multi_handedness)
``` 
en alguna parte del ciclo. Se obtiene un resultado como el de la imágen:    

![Resultado tras imprimir el valor multi_handedness](https://omes-va.com/wp-content/uploads/2021/05/handedness_output.jpeg)     
En caso de que se tengan varias manos, el resultado del print cambia y muestra la misma información para cada mano detectada:
![Múltiples manos con multi_handedness](https://omes-va.com/wp-content/uploads/2021/05/handedness_output_2hands.jpeg)               

Si no hay se detecta niniguna mano, el resultado de ```print('Handedness:', results.multi_handedness)``` será ```None```.

> Administrador. (2024, December 8). Como usar MEDIAPIPE HANDS ?️ | Python – MediaPipe – OpenCV. OMES. https://omes-va.com/mediapipe-hands-python/

## ¿Cómo se utiliza OpenCV tras obtener la información de Mediapipe?
Se traduce las coordenadas de las puntas de los dedos, que están normalizadas de 0 a 1, y se multiplica por las dimensiones de la imágen, obteniendo así una proporción que da como resultado la posición donde debería estar ese punto.
```python
        xi = int(puntaIdxIzq.x * w)
        yi = int(puntaIdxIzq.y * h)    
        xd = int(puntaIdxDer.x * w)
        yd = int(puntaIdxDer.y * h)
```
Y al final, se dibuja el rectángulo y se muestra la imágen.
```python
cv.rectangle(frame, (xi, yi), (xd, yd), (74, 89, 33), -1)
                       
    # Mostrar el video
    cv.imshow("Reconocimiento de Letras", frame)
```
Al final, OpenCV espera a que se presione la tecla Q, se libera la imágen en pantalla y se elimina la ventana
```python
    # Salir con la tecla 'q'
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar recursos
cap.release()
cv.destroyAllWindows()
```
## Resultados:
![Ejecucion](https://i.imgur.com/Opz95Hr.gif)
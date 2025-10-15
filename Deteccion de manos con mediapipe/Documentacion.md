# Deteccion de manos con libreria mediapipe de google 

Mediapipe es una herramienta pensada para facilitar la visión por computadora   
Funciona utilizando modelos ya entrenados con miles de imágenes muestra en sus datasets, y es capaz de detectar caras, manos y hasta el cuerpo completo. 


Para trabajar correctamente con mediapipe también se utiliza la libreria de OpenCV, por ejemplo, para poder ver lo que ve la cámara y trabajar con eso: 
```python
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
```
```python

 # Mostrar la imagen
    cv2.imshow("Salida", frame)

    # Salir con 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### Landmarks
Según los [apuntes de clase](https://ealcaraz85.github.io/Graficacion.io/#orgbfd06e9), los landmarks son puntos clave dentro de una imágen que ayudan a describir caracteristicas de un objeto.     
En este caso específico de las manos, se obtienen 21 landmarks que indican puntos clave de las manos, siendo estos los puntos articulados.  
![Estrucura de landmarks de la mano]("hand_landmarks.png")  

Para poder obtener estos landmarks, se utiliza el método Hands() :  
```python
# Inicializar MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
```
Se obtiene el objeto ```mp.soluions.hands```, y después se le aplica el método para obtener los landmarks de la imágen. Si no encuentra ninguna mano devuelve ```None```, de lo contrario, devuelve un array con la ubicación de cada uno de los landmarks. 

### Modelo de color y dibujar los landmarks

Mediapipe, a diferencia de OpenCV, trabaja con el modelo de color RGB, por lo que es necesario hacer la conversión de modelos durante el ciclo: 
```python
 # Convertir imagen a RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Detectar manos
    results = hands.process(frame_rgb)
```
Tras ser modificado el modelo de color, se procesa la imágen dentro y devuelve los puntos de la imágen de cada elemento.    
Después de conocer las ubicaciones, se dibujan cada uno de los puntos:
```python
    # Dibujar los puntos clave y conexiones
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
```
En este caso, el dibujo de los puntos se hace con mediapipe directamente, pero se puede lograr con OpenCV de igual manera.
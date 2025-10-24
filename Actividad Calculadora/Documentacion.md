# Calculadora Virtual con MediaPipe y OpenCV

Este proyecto implementa una calculadora virtual en tiempo real utilizando OpenCV para la interfaz y MediaPipe para la detección de manos. El control se basa en la detección de dos manos, donde una mano selecciona (puntero) y la otra confirma (clic), utilizando las etiquetas de lateralidad (`multi_handedness`) de MediaPipe.

Primero se importan las librerías necesarias: `cv2` (OpenCV), `mediapipe` y `numpy`.

```python
import cv2 as cv
import mediapipe as mp
import numpy as np
```

Luego, se inicializan los objetos de MediaPipe para la detección de manos. Es crucial establecer `max_num_hands=2` para que la librería busque y procese ambas manos simultáneamente.

```python
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7)
```

Se prepara la captura de video de la cámara (`cv.VideoCapture(0)`) y se definen las variables de estado que controlarán la lógica de la calculadora:

  * `operation_string`: Almacena el texto que se muestra en la pantalla (ej. "12+5").
  * `action_locked`: Un "seguro" booleano para evitar múltiples clics accidentales.
  * `current_selection`: Almacena qué botón está siendo apuntado por el usuario.


```python
cap = cv.VideoCapture(0)
font = cv.FONT_HERSHEY_SIMPLEX

operation_string = "" 
action_locked = False 
current_selection = None
```

## Interfaz de Usuario Relativa

Para que la calculadora se adapte a cualquier tamaño de ventana, la interfaz se define con coordenadas **relativas** (valores de 0.0 a 1.0). El diccionario `buttons` almacena la etiqueta y las coordenadas (x1, y1, x2, y2) de cada tecla. `screen_rect` define la pantalla de la calculadora.

```python
buttons = {
    '7': (0.1, 0.25, 0.2, 0.35), '8': (0.25, 0.25, 0.35, 0.35), '9': (0.4, 0.25, 0.5, 0.35), '/': (0.55, 0.25, 0.65, 0.35),
    '4': (0.1, 0.4, 0.2, 0.5),   '5': (0.25, 0.4, 0.35, 0.5),   '6': (0.4, 0.4, 0.5, 0.5),   '*': (0.55, 0.4, 0.65, 0.5),
    '1': (0.1, 0.55, 0.2, 0.65), '2': (0.25, 0.55, 0.35, 0.65), '3': (0.4, 0.55, 0.5, 0.65), '-': (0.55, 0.55, 0.65, 0.65),
    'C': (0.1, 0.7, 0.2, 0.8),   '0': (0.25, 0.7, 0.35, 0.8),   '=': (0.4, 0.7, 0.5, 0.8),   '+': (0.55, 0.7, 0.65, 0.8),
}
screen_rect = (0.1, 0.1, 0.65, 0.2)
```

Se crea una función `draw_calculator` que se encarga de dibujar la interfaz en cada frame. Esta función convierte las coordenadas relativas a coordenadas de píxeles absolutas usando el alto (`h`) y ancho (`w`) del frame. También resalta el botón seleccionado (`current_selection`) en color verde.

```python
def draw_calculator(frame, current_selection, w, h):
    
    rx1, ry1, rx2, ry2 = screen_rect
    scr_x1, scr_y1 = int(rx1 * w), int(ry1 * h)
    scr_x2, scr_y2 = int(rx2 * w), int(ry2 * h)
    
    cv.rectangle(frame, (scr_x1, scr_y1), (scr_x2, scr_y2), (200, 200, 200), -1)
    cv.rectangle(frame, (scr_x1, scr_y1), (scr_x2, scr_y2), (0, 0, 0), 2)
    
    font_scale = 1.5 
    text_size = cv.getTextSize(operation_string, font, font_scale, 2)[0]
    text_x = scr_x2 - text_size[0] - 10 
    if text_x < scr_x1: text_x = scr_x1 + 10
    cv.putText(frame, operation_string, (text_x, scr_y1 + int((scr_y2 - scr_y1) * 0.7)), 
                font, font_scale, (0, 0, 0), 2, cv.LINE_AA)
    
    for key, (rx1, ry1, rx2, ry2) in buttons.items():
        x1, y1 = int(rx1 * w), int(ry1 * h)
        x2, y2 = int(rx2 * w), int(ry2 * h)
        
        if key == current_selection:
            cv.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), -1) # Verde
        else:
            cv.rectangle(frame, (x1, y1), (x2, y2), (100, 100, 100), -1) # Gris
        
        cv.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 2)
        
        font_scale_btn = 1.5
        text_size = cv.getTextSize(key, font, font_scale_btn, 2)[0]
        text_x = x1 + (x2 - x1 - text_size[0]) // 2
        text_y = y1 + (y2 - y1 + text_size[1]) // 2
        cv.putText(frame, key, (text_x, text_y), font, font_scale_btn, (0, 0, 0), 2, cv.LINE_AA)
```

## Bucle Principal y Detección

Dentro del bucle `while`, se lee el frame, se voltea (`cv.flip`) para un efecto espejo, se obtienen sus dimensiones (`h, w`) y se convierte a `RGB` para que MediaPipe pueda procesarlo.

```python
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv.flip(frame, 1)
    h, w, _ = frame.shape 
    frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    
    results = hands.process(frame_rgb)
```

## Detección de Manos por Etiqueta (Handedness)

Esta es la parte central de la lógica. En lugar de depender del orden de detección (índice `[0]` o `[1]`), se verifica la etiqueta de lateralidad (`multi_handedness`) que proporciona MediaPipe.

Se itera sobre los resultados usando `zip` para emparejar cada `hand_landmarks` (los puntos) con su `handedness` (la etiqueta).

**Importante:** Debido a que usamos `cv.flip(frame, 1)`, la cámara actúa como un espejo. La mano **izquierda real** del usuario aparece en el lado derecho del video y MediaPipe la etiqueta como `'Right'`. La mano **derecha real** es etiquetada como `'Left'`. El código asigna los roles basándose en esto:

  * **Mano Selectora (Puntero):** La mano izquierda real, etiquetada como `'Right'`.
  * **Mano Confimadora (Click):** La mano derecha real, etiquetada como `'Left'`.

```python
    current_selection = None
    selector_hand_landmarks = None # Mano Izquierda (Pointer)
    confirmer_hand_landmarks = None # Mano Derecha (Click)

    if results.multi_hand_landmarks and results.multi_handedness:
        
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            
            label = handedness.classification[0].label
            
            if label == "Right":
                selector_hand_landmarks = hand_landmarks
            elif label == "Left":
                confirmer_hand_landmarks = hand_landmarks
```

## Lógica del Puntero y Selección

Si se detecta la mano selectora (izquierda real), se dibuja y se obtiene la posición de la punta del dedo índice (Landmark 8). Se dibuja un círculo rojo como puntero. Luego, se itera sobre el diccionario `buttons` para verificar si las coordenadas (`ix`, `iy`) del puntero están dentro de los límites de algún botón. Si es así, se guarda en `current_selection`.

```python
    if selector_hand_landmarks:
        mp_drawing.draw_landmarks(frame, selector_hand_landmarks, mp_hands.HAND_CONNECTIONS)
        
        index_tip = selector_hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        ix, iy = int(index_tip.x * w), int(index_tip.y * h)
        
        cv.circle(frame, (ix, iy), 10, (0, 0, 255), 2) 

        for key, (rx1, ry1, rx2, ry2) in buttons.items():
            x1, y1 = int(rx1 * w), int(ry1 * h)
            x2, y2 = int(rx2 * w), int(ry2 * h)
            
            if x1 < ix < x2 and y1 < iy < y2:
                current_selection = key
                break
    
    if confirmer_hand_landmarks:
        mp_drawing.draw_landmarks(frame, confirmer_hand_landmarks, mp_hands.HAND_CONNECTIONS)
```

## Máquina de Estados: "Click" y Bloqueo

Para evitar que se presionen botones continuamente, se usa una variable "seguro" (`action_locked`).

1.  **Acción (Click)**: La acción solo se ejecuta si **ambas manos** (`selector_hand_landmarks` y `confirmer_hand_landmarks`) están presentes, hay un botón seleccionado (`current_selection`) y el seguro está quitado (`not action_locked`). Inmediatamente después de ejecutar la acción (ej. añadir '7', 'C', o '='), se activa el seguro (`action_locked = True`).

2.  **Reinicio (Reset)**: El seguro se reinicia a `False` únicamente cuando la **mano de confirmación** (la derecha real) es retirada de la pantalla (`if not confirmer_hand_landmarks:`). Esto permite al usuario mover el puntero a otro botón sin desactivar el seguro.

```python
    if selector_hand_landmarks and confirmer_hand_landmarks and current_selection is not None and not action_locked:
        print(f"Acción Detectada: {current_selection}")
        
        if current_selection == 'C':
            operation_string = ""
        elif current_selection == '=':
            try:
                result = eval(operation_string)
                operation_string = str(int(result) if isinstance(result, float) and result.is_integer() else round(result, 2))
            except Exception as e:
                operation_string = "Error"
        elif current_selection in "+-*/" and operation_string and operation_string[-1] in "+-*/":
            pass 
        else:
            operation_string += current_selection
            
        action_locked = True

    if not confirmer_hand_landmarks:
        if action_locked:
            print("Seguro Reiniciado (Mano Derecha retirada).")
        action_locked = False
```

## Dibujado Final y Cierre

Finalmente, se llama a `draw_calculator` para dibujar la interfaz actualizada en el frame, se muestra el video con `cv.imshow`, y se espera la tecla 'q' para salir. Al final, se liberan los recursos.

```python
    draw_calculator(frame, current_selection, w, h)
    cv.imshow("Calculadora con Manos", frame)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()
```

## Resultados:

El resultado es una calculadora funcional donde el usuario apunta con su mano izquierda real (etiquetada como 'Right') y 'hace clic' mostrando su mano derecha real (etiquetada como 'Left'). La interfaz es relativa al tamaño de la ventana y el sistema de bloqueo evita entradas accidentales.

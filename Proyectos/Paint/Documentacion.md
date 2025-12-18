# Pizarra Virtual Avanzada: Interacción por Capas y Estampado

## Introducción

Este proyecto implementa una pizarra virtual avanzada que utiliza seguimiento por color (Color Tracking) en el espacio HSV. A diferencia de versiones anteriores, este código separa el procesamiento de visión de la interfaz gráfica (UI), evitando que la cámara detecte erróneamente los elementos dibujados en pantalla. Permite trazado libre y la creación de figuras geométricas dinámicas con un sistema de anclaje manual y retroalimentación visual del cursor.

## Estructura del Código

### Importación de Librerías

Se importan las librerías necesarias: OpenCV para visión por computadora, NumPy para el manejo de matrices y lienzos, y la librería `math` para cálculos trigonométricos necesarios en la rotación de figuras.

```python
import cv2 as cv
import numpy as np
import math
```

### Inicialización y Configuración HSV

Se inicializa la captura de video y se definen los rangos de color en el espacio HSV para la segmentación del objeto de control (por defecto, azul oscuro).

```python
camara = cv.VideoCapture(0)

# Rango HSV para el objeto de control
uBajo = np.array([100, 150, 50])
uAlto = np.array([120, 255, 255])
```

### Paleta de Colores y Variables de Estado

Se define una lista de colores disponibles y se inicializan las variables de control. Se introduce `puntoInicioFigura` para funcionar como ancla en la creación de figuras y `figura_datos_actuales` para gestionar el estampado.

```python
listaColores = [rojo, verde, azul, cyan, magenta, amarillo, blanco, gris]
colorActual = verde

lienzo = None
modo = "pintar"         # "pintar" o "figura"
tipoFigura = "circulo"  # "circulo", "rectangulo", "linea"
puntoInicioFigura = None 
figura_datos_actuales = None
```

## Bucle Principal

El ciclo procesa cada cuadro en tres etapas secuenciales: Captura, Detección (Visión) y Composición (Interfaz).

### 1\. Detección y Procesamiento (Capa Invisible)

Se realiza la conversión a HSV y la creación de la máscara **antes** de dibujar cualquier elemento de la interfaz. Esto asegura que la barra de colores o los dibujos no interfieran con la detección del objeto.

```python
hsv = cv.cvtColor(cuadro, cv.COLOR_BGR2HSV)
mascara = cv.inRange(hsv, uBajo, uAlto)

# Operaciones morfológicas para limpiar ruido
kernel = np.ones((5, 5), np.uint8)
mascara = cv.morphologyEx(mascara, cv.MORPH_OPEN, kernel)
mascara = cv.morphologyEx(mascara, cv.MORPH_CLOSE, kernel)

momentos = cv.moments(mascara)
```

### 2\. Lógica de Interacción

Si se detecta un objeto (Landmark), se decide la acción según su posición.

**Selección de Color:**
Si el Landmark se encuentra en la zona superior (donde se dibujará la barra), se cambia el color actual y se reinician los puntos de trazado.

```python
if cy < altoBarra:
    indice_del_color = cx // anchoColor
    colorActual = listaColores[indice_del_color]
    puntoAnterior = None 
    puntoInicioFigura = None
```

**Modo Pintar (Trazado Libre):**
Dibuja líneas continuas en el `lienzo` (capa persistente) siguiendo el movimiento del Landmark.

```python
elif modo == "pintar":
    if puntoAnterior is not None:
        distancia = np.linalg.norm(np.array(punto_actual) - np.array(puntoAnterior))
        if distancia < umbralDistancia:
            cv.line(lienzo, puntoAnterior, punto_actual, colorActual, 5)
    puntoAnterior = punto_actual
```

### 3\. Composición Visual y Previsualización

Se combinan las capas: el cuadro de video original y el lienzo de dibujo. Posteriormente, se dibuja la **Interfaz de Usuario (UI)** sobre esta combinación.

**Previsualización y Anclaje:**

En el modo figura, la interfaz proporciona retroalimentación visual en dos estados:

1.  **Estado "Esperando Ancla":** Si no se ha presionado 'S', se muestra un icono pequeño de la herramienta seleccionada sobre el cursor junto con la instrucción "S: Anclar".
2.  **Estado "Anclado":** Una vez establecido el `puntoInicioFigura`, se visualiza la transformación dinámica (escala y rotación) de la figura.

<!-- end list -->

```python
if modo == "figura" and punto_actual[1] > altoBarra:
    
    # CASO A: Ancla establecida -> Transformación Dinámica
    if puntoInicioFigura is not None:
        # Escala basada en movimiento vertical
        movimiento_y = abs(punto_actual[1] - puntoInicioFigura[1])
        escala = max(10, min(200, movimiento_y // 2))
        
        # Ángulo basado en movimiento horizontal
        movimiento_x = punto_actual[0] - puntoInicioFigura[0]
        angulo = movimiento_x % 360

        # Dibujo de figura dinámica (Ejemplo Círculo)
        if tipoFigura == "circulo":
            cv.circle(combinado, puntoInicioFigura, escala, colorActual, 2)
            # ... código de línea de rotación ...

    # CASO B: Sin Ancla -> Icono de Herramienta
    else:
        cx, cy = punto_actual
        radio_icono = 15
        
        # Indicador visual
        cv.putText(combinado, "S: Anclar", (cx + 20, cy), cv.FONT_HERSHEY_SIMPLEX, 0.5, (200,200,200), 1)

        if tipoFigura == "circulo":
            cv.circle(combinado, punto_actual, radio_icono, colorActual, 2)
        elif tipoFigura == "rectangulo":
            cv.rectangle(combinado, (cx - radio_icono, cy - 10), (cx + radio_icono, cy + 10), colorActual, 2)
        # ... lógica para línea ...
```

### Controles y Estampado

Se gestionan los eventos de teclado para controlar la aplicación. Se destaca la funcionalidad de **Estampado ('E')**, que fija la figura previsualizada en el lienzo permanente.

```python
tecla = cv.waitKey(1) & 0xFF

if tecla == ord('s'):  # Establecer punto de ancla
    puntoInicioFigura = punto_actual

elif tecla == ord('e') or tecla == 32:  # Estampar figura
    if modo == "figura" and figura_datos_actuales is not None:
        # Se dibuja permanentemente en la capa 'lienzo'
        d = figura_datos_actuales
        if d['tipo'] == 'circulo':
            cv.circle(lienzo, d['c'], d['r'], d['col'], 2)
        elif d['tipo'] == 'rectangulo':
            cv.drawContours(lienzo, [d['box']], 0, d['col'], 2)
        
        puntoInicioFigura = None  # Reiniciar para la siguiente figura
```

## Resultados

La aplicación corrige los problemas de interferencia visual al separar las capas de procesamiento y visualización. La experiencia de usuario mejora significativamente con el indicador de herramienta flotante, que permite saber qué figura se va a crear antes de fijar el punto de anclaje, facilitando la composición precisa de escenas geométricas.

## Referencias

  - OpenCV Documentation: [https://docs.opencv.org/](https://docs.opencv.org/)
  - NumPy Documentation: [https://numpy.org/doc/](https://numpy.org/doc/)
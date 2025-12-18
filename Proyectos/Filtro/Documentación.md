# Filtro de Realidad Aumentada: Máscara Cyborg con Anclaje Dual

## Introducción

Este proyecto desarrolla un filtro de realidad aumentada (AR) que superpone una máscara estilo "cyborg" sobre el rostro del usuario en tiempo real. Utiliza la librería MediaPipe Face Mesh para la detección de puntos faciales (landmarks) y OpenGL para el renderizado de gráficos vectoriales.

Una característica técnica relevante de esta implementación es el uso de un anclaje dual: la parte superior del visor se posiciona relativa al entrecejo (Landmark 6), mientras que la placa inferior se ancla independientemente a la barbilla (Landmark 152), permitiendo la articulación de la máscara con el movimiento de la mandíbula.

## Estructura del Código

### Importación de Librerías

Se utilizan librerías para gráficos, matemáticas y visión por computadora.

```python
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import cv2
import mediapipe as mp
import numpy as np
import math
import random
```

### Inicialización y Configuración

Se configura MediaPipe Face Mesh con la opción `refine_landmarks=True` para obtener mayor precisión en el contorno de ojos y labios. Asimismo, se inicializa el contexto de OpenGL con proyección ortográfica (`glOrtho`) para trabajar en un espacio de coordenadas 2D alineado con la cámara.

```python
# Inicialización de MediaPipe
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

# Configuración de OpenGL
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
```

### Sistema de Partículas (Fondo)

Se define la clase `NumeroBinario` para gestionar la animación de fondo, simulando una caída de caracteres binarios ('0' y '1') con velocidades y posiciones aleatorias.

```python
class NumeroBinario:
    def __init__(self):
        self.x = random.uniform(-0.6, 0.6)
        self.y = random.uniform(0.8, 1.2)
        # ... inicialización de velocidad y valor
```

## Lógica de Renderizado

### Geometría Procedural

Los elementos gráficos se generan mediante funciones que utilizan primitivas de OpenGL (`GL_LINES`, `GL_QUADS`, `GL_TRIANGLE_FAN`), evitando la dependencia de modelos 3D externos.

Se definen funciones modulares para cada componente:

  * `dibujar_visor_principal()`: Renderiza la estructura superior.
  * `dibujar_trapecio_barbilla_152()`: Renderiza la placa inferior.
  * `dibujar_hud_elementos()`: Dibuja la interfaz gráfica lateral.

### Transformación de Coordenadas

Las coordenadas normalizadas de MediaPipe (0.0 a 1.0) se transforman al sistema de coordenadas de OpenGL (-1.0 a 1.0) para su correcta visualización en la ventana.

```python
# Conversión de coordenadas del Landmark de anclaje (Ej. Landmark 6)
gl_x_visor = (visor_anchor.x - 0.5) * 2
gl_y_visor = -(visor_anchor.y - 0.5) * 2
```

## Bucle Principal y Anclaje Dual

El ciclo principal captura el video, actualiza las animaciones y procesa la malla facial. La lógica de posicionamiento se divide en dos bloques independientes.

### 1\. Cálculo de Transformaciones

Se calculan los parámetros de transformación espacial basándose en la geometría facial detectada:

  * **Escala:** Proporcional a la distancia entre los ojos.
  * **Rotación (Roll):** Ángulo formado por la línea de los ojos.
  * **Rotación (Yaw):** Estimación basada en la posición horizontal de la nariz.

### 2\. Renderizado del Bloque Superior

Se utiliza una matriz de transformación (`glPushMatrix`) anclada al **Landmark 6** (Glabela). Esto fija el visor a la frente del usuario, asegurando estabilidad ante cambios de profundidad.

```python
glPushMatrix()
glTranslatef(gl_x_visor, gl_y_visor, 0) # Traslación al entrecejo
glScalef(scale, scale, scale)
glRotatef(-angle_roll, 0, 0, 1)
glRotatef(angle_yaw, 0, 1, 0)
dibujar_cyborg(..., 0)
glPopMatrix()
```

### 3\. Renderizado del Bloque Inferior

Se utiliza una segunda matriz independiente anclada al **Landmark 152** (Barbilla). Esto permite que la placa inferior siga el movimiento de la mandíbula sin deformar la parte superior de la máscara.

```python
glPushMatrix()
glTranslatef(gl_x_chin, gl_y_chin, 0)   # Traslación a la barbilla
glScalef(scale, scale, scale)
glRotatef(-angle_roll, 0, 0, 1)
glRotatef(angle_yaw, 0, 1, 0)
dibujar_trapecio_barbilla_152()
glPopMatrix()
```

### Detección de Estado (Modo Alerta)

El sistema monitorea la apertura de la boca calculando la distancia vertical entre los labios. Si esta supera un umbral predefinido, se altera el estado de la aplicación (`modo_alerta`), cambiando la paleta de colores de cyan a rojo.

```python
apertura_boca = abs(landmarks[13].y - landmarks[14].y) * 100
modo_alerta = True if apertura_boca > 1.5 else False
```

## Resultados

La implementación logra una superposición gráfica estable y reactiva. La separación de matrices de transformación para la parte superior e inferior del rostro permite una simulación mecánica coherente con la anatomía facial, manteniendo la integridad visual del filtro durante el movimiento y la gesticulación.

## Referencias

  - MediaPipe Face Mesh: [https://google.github.io/mediapipe/solutions/face\_mesh.html](https://www.google.com/search?q=https://google.github.io/mediapipe/solutions/face_mesh.html)
  - PyOpenGL Documentation: [http://pyopengl.sourceforge.net/documentation/](http://pyopengl.sourceforge.net/documentation/)
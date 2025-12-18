import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import cv2
import mediapipe as mp
import numpy as np
import math
import random

# Variables globales
window = None
video_texture_id = None

# Variables de animación
brillo_led = 0.0
direccion_brillo = 1
posicion_escaneo = -1.0
direccion_escaneo = 1
parpadeo_leds = 0
contador_parpadeo = 0
modo_alerta = False
numeros_binarios = []

class NumeroBinario:
    def __init__(self):
        self.x = random.uniform(-0.6, 0.6)
        self.y = random.uniform(0.8, 1.2)
        self.velocidad = random.uniform(0.01, 0.03)
        self.valor = random.choice(['0', '1'])
        self.opacidad = random.uniform(0.3, 0.8)
        
    def actualizar(self):
        self.y -= self.velocidad
        if self.y < -1.2:
            self.y = 1.2
            self.x = random.uniform(-0.6, 0.6)
            self.valor = random.choice(['0', '1'])

for _ in range(20):
    numeros_binarios.append(NumeroBinario())

# Mediapipe
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

cap = cv2.VideoCapture(0)

# OpenGL 
def init_opengl(width, height):
    global video_texture_id
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-1, 1, -1, 1, -10, 10)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    glEnable(GL_TEXTURE_2D)
    video_texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, video_texture_id)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

def dibujar_fondo(frame):
    height, width, _ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_data = cv2.flip(frame_rgb, 0)
    
    glDisable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, video_texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, frame_data)
    
    glColor3f(1, 1, 1)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex3f(-1, -1, 0)
    glTexCoord2f(1, 0); glVertex3f( 1, -1, 0)
    glTexCoord2f(1, 1); glVertex3f( 1,  1, 0)
    glTexCoord2f(0, 1); glVertex3f(-1,  1, 0)
    glEnd()
    glDisable(GL_TEXTURE_2D)

# Geometría básica
def dibujar_hexagono(radio):
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(0, 0)
    for i in range(7):
        angulo = math.pi / 3 * i
        glVertex2f(radio * math.cos(angulo), radio * math.sin(angulo))
    glEnd()

def dibujar_circulo(radio, segmentos=30):
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(0, 0)
    for i in range(segmentos + 1):
        angulo = 2 * math.pi * i / segmentos
        glVertex2f(radio * math.cos(angulo), radio * math.sin(angulo))
    glEnd()

def dibujar_lineas_circuito(x, y, tam, horizontal=True):
    glLineWidth(2)
    glBegin(GL_LINES)
    if horizontal:
        glVertex2f(x, y); glVertex2f(x + tam, y)
        glVertex2f(x + tam * 0.3, y); glVertex2f(x + tam * 0.3, y + tam * 0.15)
        glVertex2f(x + tam * 0.7, y); glVertex2f(x + tam * 0.7, y - tam * 0.15)
    else:
        glVertex2f(x, y); glVertex2f(x, y + tam)
        glVertex2f(x, y + tam * 0.3); glVertex2f(x + tam * 0.15, y + tam * 0.3)
        glVertex2f(x, y + tam * 0.7); glVertex2f(x - tam * 0.15, y + tam * 0.7)
    glEnd()
    glLineWidth(1)

# Cyborg
def dibujar_visor_principal(brillo, parpadeo, modo_alerta, eye_level_y=0):
    cyan_oscuro = (0.0, 0.3, 0.4)
    cyan = (0.0, 0.7 + brillo * 0.3, 1.0)
    cyan_brillante = (0.5, 1.0, 1.0)
    rojo = (1.0, 0.0, 0.0)
    rojo_brillante = (1.0, 0.3, 0.0)
    
    if modo_alerta:
        color_principal = rojo
        color_brillo = rojo_brillante
    else:
        color_principal = cyan
        color_brillo = cyan_brillante
    
    vertical_offset = eye_level_y 
    
    glColor4f(*cyan_oscuro, 0.7)
    glBegin(GL_QUADS)
    glVertex2f(-0.55, 0.18 + vertical_offset); glVertex2f(0.55, 0.18 + vertical_offset)
    glVertex2f(0.5, -0.05 + vertical_offset); glVertex2f(-0.5, -0.05 + vertical_offset)
    glEnd()
    
    glColor4f(*color_principal, 0.9)
    glLineWidth(3)
    glBegin(GL_LINE_STRIP)
    glVertex2f(-0.55, 0.18 + vertical_offset); glVertex2f(0.55, 0.18 + vertical_offset)
    glVertex2f(0.5, -0.05 + vertical_offset); glVertex2f(-0.5, -0.05 + vertical_offset)
    glVertex2f(-0.55, 0.18 + vertical_offset)
    glEnd()
    glLineWidth(1)
    
    if parpadeo == 0:
        glPushMatrix()
        glTranslatef(-0.25, 0.065 + vertical_offset, 0.01)
        glColor4f(*color_brillo, 0.8 + brillo * 0.2)
        dibujar_hexagono(0.08)
        glColor4f(*color_principal, 0.9)
        dibujar_hexagono(0.06)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0.25, 0.065 + vertical_offset, 0.01)
        glColor4f(*color_brillo, 0.8 + brillo * 0.2)
        dibujar_hexagono(0.08)
        glColor4f(*color_principal, 0.9)
        dibujar_hexagono(0.06)
        glPopMatrix()
    
    glColor4f(*color_principal, 0.6)
    glLineWidth(1)
    glBegin(GL_LINES)
    for i in range(4):
        y_pos = 0.14 - i * 0.05 + vertical_offset
        glVertex2f(-0.5, y_pos); glVertex2f(-0.15, y_pos)
        glVertex2f(0.15, y_pos); glVertex2f(0.5, y_pos)
    glEnd()

def dibujar_placa_temporal(lado, eye_level_y=0):
    gris = (0.5, 0.5, 0.6)
    gris_oscuro = (0.3, 0.3, 0.35)
    cyan = (0.0, 0.8, 1.0)
    
    x = 0.45 * lado
    vertical_offset = eye_level_y * 0.8
    
    glPushMatrix()
    glTranslatef(x, 0.15 + vertical_offset, 0.02)
    
    glColor4f(*gris, 0.8)
    glBegin(GL_QUADS)
    glVertex2f(-0.08 * lado, 0.15); glVertex2f(0.0, 0.15)
    glVertex2f(0.0, -0.1); glVertex2f(-0.08 * lado, -0.1)
    glEnd()
    
    glColor4f(*gris_oscuro, 0.7)
    for i in range(3):
        y = 0.1 - i * 0.07
        glBegin(GL_QUADS)
        glVertex2f(-0.07 * lado, y); glVertex2f(-0.01 * lado, y)
        glVertex2f(-0.01 * lado, y - 0.03); glVertex2f(-0.07 * lado, y - 0.03)
        glEnd()
    
    glColor4f(*cyan, 0.9)
    for i in range(3):
        glPushMatrix()
        glTranslatef(-0.04 * lado, 0.08 - i * 0.07, 0.01)
        dibujar_circulo(0.008)
        glPopMatrix()
    
    glPopMatrix()

def dibujar_circuitos_mejilla(lado, eye_level_y=0):
    cyan = (0.0, 0.8, 1.0)
    x = 0.3 * lado
    vertical_offset = eye_level_y
    
    glColor4f(*cyan, 0.6)
    dibujar_lineas_circuito(x, -0.05 + vertical_offset, 0.15 * lado, True)
    dibujar_lineas_circuito(x, -0.15 + vertical_offset, 0.12 * lado, True)
    
    glColor4f(*cyan, 0.8)
    glPointSize(4)
    glBegin(GL_POINTS)
    glVertex2f(x, -0.05 + vertical_offset); glVertex2f(x + 0.05 * lado, -0.05 + vertical_offset)
    glVertex2f(x + 0.10 * lado, -0.05 + vertical_offset)
    glVertex2f(x, -0.15 + vertical_offset); glVertex2f(x + 0.08 * lado, -0.15 + vertical_offset)
    glEnd()
    glPointSize(1)

def dibujar_linea_escaneo(posicion, brillo, eye_level_y=0):
    rojo = (1.0, 0.0, 0.0)
    amarillo = (1.0, 1.0, 0.0)
    y = posicion + eye_level_y
    
    glColor4f(*rojo, 0.7)
    glLineWidth(2)
    glBegin(GL_LINES); glVertex2f(-0.6, y); glVertex2f(0.6, y); glEnd()
    
    glColor4f(*amarillo, 0.5 + brillo * 0.3)
    glLineWidth(4)
    glBegin(GL_LINES); glVertex2f(-0.6, y); glVertex2f(0.6, y); glEnd()
    glLineWidth(1)
    
    glColor4f(*rojo, 0.4)
    glBegin(GL_LINES)
    glVertex2f(-0.6, y + 0.01); glVertex2f(0.6, y + 0.01)
    glVertex2f(-0.6, y - 0.01); glVertex2f(0.6, y - 0.01)
    glEnd()

def dibujar_hud_elementos(eye_level_y=0):
    verde = (0.0, 1.0, 0.0)
    cyan = (0.0, 0.8, 1.0)
    vertical_offset = eye_level_y * 0.5
    
    glColor4f(*verde, 0.6)
    glLineWidth(2)
    
    glBegin(GL_LINE_STRIP); glVertex2f(-0.7, 0.5 + vertical_offset); glVertex2f(-0.6, 0.5 + vertical_offset); glVertex2f(-0.6, 0.4 + vertical_offset); glEnd()
    glBegin(GL_LINE_STRIP); glVertex2f(-0.7, 0.4 + vertical_offset); glVertex2f(-0.7, 0.5 + vertical_offset); glEnd()
    
    glBegin(GL_LINE_STRIP); glVertex2f(0.7, 0.5 + vertical_offset); glVertex2f(0.6, 0.5 + vertical_offset); glVertex2f(0.6, 0.4 + vertical_offset); glEnd()
    glBegin(GL_LINE_STRIP); glVertex2f(0.7, 0.4 + vertical_offset); glVertex2f(0.7, 0.5 + vertical_offset); glEnd()
    
    glBegin(GL_LINE_STRIP); glVertex2f(-0.7, -0.5 + vertical_offset); glVertex2f(-0.6, -0.5 + vertical_offset); glVertex2f(-0.6, -0.4 + vertical_offset); glEnd()
    glBegin(GL_LINE_STRIP); glVertex2f(-0.7, -0.4 + vertical_offset); glVertex2f(-0.7, -0.5 + vertical_offset); glEnd()
    
    glBegin(GL_LINE_STRIP); glVertex2f(0.7, -0.5 + vertical_offset); glVertex2f(0.6, -0.5 + vertical_offset); glVertex2f(0.6, -0.4 + vertical_offset); glEnd()
    glBegin(GL_LINE_STRIP); glVertex2f(0.7, -0.4 + vertical_offset); glVertex2f(0.7, -0.5 + vertical_offset); glEnd()
    
    glColor4f(*cyan, 0.5)
    for i in range(5):
        y_pos = 0.3 - i * 0.12 + vertical_offset
        ancho = 0.05 + (i % 3) * 0.03
        glBegin(GL_QUADS)
        glVertex2f(0.65, y_pos); glVertex2f(0.65 + ancho, y_pos)
        glVertex2f(0.65 + ancho, y_pos - 0.02); glVertex2f(0.65, y_pos - 0.02)
        glEnd()
    glLineWidth(1)

# Fijar trapecio barbilla 152
def dibujar_trapecio_barbilla_152():
    """Dibuja el trapecio con 5 puntos, centrado en (0,0) para ser anclado."""
    gris_oscuro = (0.3, 0.3, 0.35)
    cyan = (0.0, 0.8, 1.0)

    top_w = 0.4
    bot_w = 0.2
    h = 0.15
    y_top = h / 2
    y_bot = -h / 2

    # 1. Placa base
    glColor4f(*gris_oscuro, 0.85)
    glBegin(GL_QUADS)
    glVertex2f(-top_w/2, y_top); glVertex2f(top_w/2, y_top)
    glVertex2f(bot_w/2, y_bot);  glVertex2f(-bot_w/2, y_bot)
    glEnd()

    # 2. Borde Neón
    glColor4f(*cyan, 0.9)
    glLineWidth(2)
    glBegin(GL_LINE_LOOP)
    glVertex2f(-top_w/2, y_top); glVertex2f(top_w/2, y_top)
    glVertex2f(bot_w/2, y_bot);  glVertex2f(-bot_w/2, y_bot)
    glEnd()
    glLineWidth(1)

    # 3. Los 5 Puntos
    spacing = 0.07
    for i in range(5):
        x_pos = (i - 2) * spacing
        glPushMatrix()
        glTranslatef(x_pos, 0, 0.01) 
        dibujar_circulo(0.015)
        glPopMatrix()

def dibujar_numeros_binarios():
    verde = (0.0, 1.0, 0.2)
    for num in numeros_binarios:
        glColor4f(*verde, num.opacidad)
        glPushMatrix()
        glTranslatef(num.x, num.y, -0.5)
        glScalef(0.03, 0.03, 1)
        if num.valor == '1':
            glBegin(GL_LINES); glVertex2f(0, -1); glVertex2f(0, 1); glEnd()
        else:
            glBegin(GL_LINE_LOOP)
            for i in range(20):
                angle = 2*math.pi*i/20
                glVertex2f(0.7*math.cos(angle), math.sin(angle))
            glEnd()
        glPopMatrix()

# Dibujo Cyborg Completo
def dibujar_cyborg(brillo, posicion_escaneo, parpadeo, modo_alerta, eye_level_y=0):
    glEnable(GL_DEPTH_TEST)
    dibujar_visor_principal(brillo, parpadeo, modo_alerta, eye_level_y)
    dibujar_placa_temporal(-1, eye_level_y)
    dibujar_placa_temporal(1, eye_level_y)
    dibujar_circuitos_mejilla(-1, eye_level_y)
    dibujar_circuitos_mejilla(1, eye_level_y)
    dibujar_linea_escaneo(posicion_escaneo, brillo, eye_level_y)
    dibujar_hud_elementos(eye_level_y)

def main():
    global window, brillo_led, direccion_brillo, posicion_escaneo, direccion_escaneo
    global parpadeo_leds, contador_parpadeo, modo_alerta
    
    if not glfw.init(): return
    window = glfw.create_window(800, 600, "Cyborg Mask - Visor on Landmark 6", None, None)
    if not window: glfw.terminate(); return
    glfw.make_context_current(window)
    init_opengl(800, 600)
    
    while not glfw.window_should_close(window):
        ret, frame = cap.read()
        if not ret: break
        frame = cv2.flip(frame, 1)
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        dibujar_fondo(frame)
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Animaciones
        brillo_led += 0.04 * direccion_brillo
        if brillo_led >= 1.0 or brillo_led <= 0.0: direccion_brillo *= -1
        posicion_escaneo += 0.03 * direccion_escaneo
        if posicion_escaneo >= 0.5 or posicion_escaneo <= -0.5: direccion_escaneo *= -1
        contador_parpadeo += 1
        if contador_parpadeo > 50: contador_parpadeo = 0
        parpadeo_leds = 1 if contador_parpadeo > 45 else 0
        for num in numeros_binarios: num.actualizar()
        
        res_face = face_mesh.process(rgb_frame)
        
        if res_face.multi_face_landmarks:
            landmarks = res_face.multi_face_landmarks[0].landmark
            
            # Puntos de anclaje
            # Visor Superior: Landmark 6 (Entre los ojos/cejas)
            visor_anchor = landmarks[6]
            
            # Barbilla: Landmark 152
            chin_landmark = landmarks[152]
            
            # Ojos y labios para otros cálculos (escala/rotación)
            left_eye_center = ((landmarks[33].x + landmarks[133].x)/2, (landmarks[33].y + landmarks[133].y)/2)
            right_eye_center = ((landmarks[362].x + landmarks[263].x)/2, (landmarks[362].y + landmarks[263].y)/2)
            
            # Coordenadas OpenGL
            # 1. Ancla Visor (Landmark 6)
            gl_x_visor = (visor_anchor.x - 0.5) * 2
            gl_y_visor = -(visor_anchor.y - 0.5) * 2
            
            # 2. Ancla Barbilla (Landmark 152)
            gl_x_chin = (chin_landmark.x - 0.5) * 2
            gl_y_chin = -(chin_landmark.y - 0.5) * 2

            # Cálculos de Escala y Rotación
            eye_distance = np.linalg.norm([left_eye_center[0] - right_eye_center[0], left_eye_center[1] - right_eye_center[1]])
            scale = eye_distance * 4.0
            
            delta_x = right_eye_center[0] - left_eye_center[0]
            delta_y = right_eye_center[1] - left_eye_center[1]
            angle_roll = np.degrees(np.arctan2(delta_y, delta_x))
            angle_yaw = (landmarks[4].x - (left_eye_center[0] + right_eye_center[0])/2) * 180
            
            apertura_boca = abs(landmarks[13].y - landmarks[14].y) * 100
            modo_alerta = True if apertura_boca > 1.5 else False
            
            # Renderizado 
            glDisable(GL_DEPTH_TEST)
            dibujar_numeros_binarios()
            glEnable(GL_DEPTH_TEST)
            
            # Visor superior
            glPushMatrix()
            # Traslación CORRECTA a coordenadas absolutas del punto 6
            glTranslatef(gl_x_visor, gl_y_visor, 0)
            glScalef(scale, scale, scale)
            glRotatef(-angle_roll, 0, 0, 1)
            glRotatef(angle_yaw, 0, 1, 0)
            # Pasamos 0 como offset vertical porque ya trasladamos el origen al punto 6
            dibujar_cyborg(brillo_led, posicion_escaneo, parpadeo_leds, modo_alerta, 0)
            glPopMatrix()

            # Babrilla
            glPushMatrix()
            glTranslatef(gl_x_chin, gl_y_chin, 0)
            glScalef(scale, scale, scale)
            glRotatef(-angle_roll, 0, 0, 1)
            glRotatef(angle_yaw, 0, 1, 0)
            dibujar_trapecio_barbilla_152()
            glPopMatrix()
        
        glfw.swap_buffers(window)
        glfw.poll_events()
    
    cap.release()
    glfw.terminate()

if __name__ == "__main__":
    main()
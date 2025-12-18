import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import sys
import math

window = None
angle = 0 

def init():
    # Configuración inicial de OpenGL
    glClearColor(0.0, 0.0, 0.0, 1.0)  # Color de fondo
    glEnable(GL_DEPTH_TEST)
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1.0, 0.1, 70.0)
    glMatrixMode(GL_MODELVIEW)
    
def draw_pyramid():
    global angle
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    puntaArriba = (1/2, math.sqrt(6)/3, math.sqrt(3)/6)
    puntaIzq = (1, 0, 0)
    puntaDer = (1/2, 0, math.sqrt(3)/2)
    puntaFrente = (0, 0, 0)
    
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -5)
    glRotatef(angle, 1, 1, 1)
    
    glBegin(GL_TRIANGLES)
    
    glColor3f(1.0, 0.0, 0.0)  # Rojo
    glVertex3f(*puntaArriba)
    glVertex3f(*puntaIzq)
    glVertex3f(*puntaDer) 
    
    glColor3f(0.0, 1.0, 0.0) # Verde
    glVertex3f(*puntaArriba)
    glVertex3f(*puntaDer)
    glVertex3f(*puntaFrente)
    
    glColor3f(0.0, 0.0, 1.0) # Azul
    glVertex3f(*puntaArriba)
    glVertex3f(*puntaFrente)
    glVertex3f(*puntaIzq)
    
    glColor3f(1.0, 1.0, 0.0) # Amarillo
    glVertex3f(*puntaIzq)
    glVertex3f(*puntaFrente)
    glVertex3f(*puntaDer)

    glEnd()
    glFlush()
    glfw.swap_buffers(window)
    angle += 0.1  # Incrementar el ángulo para rotación
    
def main():
    global window
    if not glfw.init():
        print("No se pudo inicializar GLFW")
        sys.exit(1)
    
    window = glfw.create_window(800, 600, "Piramide Rotatoria", None, None)
    if not window:
        glfw.terminate()
        print("No se pudo crear la ventana")
        sys.exit(1)
    
    glfw.make_context_current(window)
    init()
    
    while not glfw.window_should_close(window):
        draw_pyramid()
        glfw.poll_events()
    
    glfw.terminate()
    
if __name__ == "__main__":
    main()
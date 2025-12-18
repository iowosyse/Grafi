import cv2 as cv
import numpy as np
import math

# --- INICIALIZACIÓN ---
camara = cv.VideoCapture(0)

# Rango HSV (Azul oscuro)
uBajo = np.array([100, 150, 50])
uAlto = np.array([120, 255, 255])

# Colores (BGR)
rojo = (0, 0, 255)
verde = (0, 255, 0)
azul = (255, 0, 0)
cyan = (255, 255, 0)
magenta = (255, 0, 255)
amarillo = (0, 255, 255)
blanco = (255, 255, 255)
gris = (118, 118, 118)

listaColores = [rojo, verde, azul, cyan, magenta, amarillo, blanco, gris]
nombresColores = ["Rojo", "Verde", "Azul", "Cyan", "Magenta", "Amarillo", "Blanco", "Gris"]
colorActual = verde
indice_color = 1

# Variables de Control
lienzo = None
modo = "pintar"         
tipoFigura = "circulo"  
puntoAnterior = None    
puntoInicioFigura = None 
umbralDistancia = 50

# Variables temporales para el estampado
figura_datos_actuales = None 

print("--- CONTROLES ---")
print("'M': Cambiar Modo (Pintar/Figura)")
print("'S': Establecer Punto de Inicio (Ancla)")
print("'F': Cambiar Tipo de Figura")
print("'E' o ESPACIO: Estampar figura")
print("'C': Limpiar | 'ESC': Salir")

while True:
    # 1. CAPTURA
    ret, cuadro = camara.read()
    if not ret: break
    cuadro = cv.flip(cuadro, 1)
    alto, ancho, _ = cuadro.shape

    if lienzo is None:
        lienzo = np.zeros_like(cuadro)

    # 2. PROCESAMIENTO
    hsv = cv.cvtColor(cuadro, cv.COLOR_BGR2HSV)
    mascara = cv.inRange(hsv, uBajo, uAlto)

    kernel = np.ones((5, 5), np.uint8)
    mascara = cv.morphologyEx(mascara, cv.MORPH_OPEN, kernel)
    mascara = cv.morphologyEx(mascara, cv.MORPH_CLOSE, kernel)

    momentos = cv.moments(mascara)
    punto_actual = None

    if momentos["m00"] > 0:
        cx = int(momentos["m10"] / momentos["m00"])
        cy = int(momentos["m01"] / momentos["m00"])
        punto_actual = (cx, cy)

        # Lógica de Barra
        altoBarra = 60
        anchoColor = ancho // len(listaColores)
        
        if cy < altoBarra:
            indice_del_color = cx // anchoColor
            if 0 <= indice_del_color < len(listaColores):
                colorActual = listaColores[indice_del_color]
                puntoAnterior = None 
                puntoInicioFigura = None
        else:
            # Modo Pintar
            if modo == "pintar":
                if puntoAnterior is not None:
                    distancia = np.linalg.norm(np.array(punto_actual) - np.array(puntoAnterior))
                    if distancia < umbralDistancia:
                        cv.line(lienzo, puntoAnterior, punto_actual, colorActual, 5)
                puntoAnterior = punto_actual
            
            # Modo Figura
            elif modo == "figura":
                puntoAnterior = None
                pass 

    else:
        puntoAnterior = None

    # 3. COMPOSICIÓN Y VISUALIZACIÓN
    combinado = cv.add(cuadro, lienzo)

    # Barra de colores
    altoBarra = 60
    anchoColor = ancho // len(listaColores)
    cv.rectangle(combinado, (0,0), (ancho, altoBarra), (50,50,50), -1)

    for i, color in enumerate(listaColores):
        xInicio = i * anchoColor
        xFin = (i + 1) * anchoColor
        cv.rectangle(combinado, (xInicio, 5), (xFin, altoBarra-5), color, -1)
        if color == colorActual:
             cv.rectangle(combinado, (xInicio, 5), (xFin, altoBarra-5), (255, 255, 255), 3)

    # --- DIBUJO DE INTERFAZ ---
    if punto_actual is not None:
        # Puntero básico
        cv.circle(combinado, punto_actual, 5, (0, 0, 255), -1)

        # Si estamos en modo FIGURA y debajo de la barra...
        if modo == "figura" and punto_actual[1] > altoBarra:
            
            # CASO A: YA TENEMOS ANCLA ('S' fue presionado) -> DIBUJAR DINÁMICO
            if puntoInicioFigura is not None:
                movimiento_y = abs(punto_actual[1] - puntoInicioFigura[1])
                escala = max(10, min(200, movimiento_y // 2))
                
                movimiento_x = punto_actual[0] - puntoInicioFigura[0]
                angulo = movimiento_x % 360

                # Dibujar Ancla
                cv.circle(combinado, puntoInicioFigura, 3, (255, 255, 255), -1)
                cv.line(combinado, puntoInicioFigura, punto_actual, (100, 100, 100), 1)

                if tipoFigura == "circulo":
                    cv.circle(combinado, puntoInicioFigura, escala, colorActual, 2)
                    end_x = int(puntoInicioFigura[0] + escala * math.cos(math.radians(angulo)))
                    end_y = int(puntoInicioFigura[1] + escala * math.sin(math.radians(angulo)))
                    cv.line(combinado, puntoInicioFigura, (end_x, end_y), colorActual, 2)
                    figura_datos_actuales = {'tipo': 'circulo', 'c': puntoInicioFigura, 'r': escala, 'col': colorActual}

                elif tipoFigura == "rectangulo":
                    rect = ((puntoInicioFigura[0], puntoInicioFigura[1]), (escala * 2, escala), angulo)
                    box = cv.boxPoints(rect)
                    box = np.int0(box)
                    cv.drawContours(combinado, [box], 0, colorActual, 2)
                    figura_datos_actuales = {'tipo': 'rectangulo', 'box': box, 'col': colorActual}

                elif tipoFigura == "linea":
                    cv.line(combinado, puntoInicioFigura, punto_actual, colorActual, 5)
                    figura_datos_actuales = {'tipo': 'linea', 'p1': puntoInicioFigura, 'p2': punto_actual, 'col': colorActual}

            # CASO B: NO HAY ANCLA AÚN -> MOSTRAR ICONO FLOTANTE PEQUEÑO
            else:
                cx, cy = punto_actual
                radio_icono = 15 # Tamaño pequeño
                
                # Indicador visual de "Esperando Ancla"
                cv.putText(combinado, "S: Anclar", (cx + 20, cy), cv.FONT_HERSHEY_SIMPLEX, 0.5, (200,200,200), 1)

                if tipoFigura == "circulo":
                    cv.circle(combinado, punto_actual, radio_icono, colorActual, 2)
                
                elif tipoFigura == "rectangulo":
                    # Dibujar un rectángulo pequeño centrado en el puntero
                    cv.rectangle(combinado, (cx - radio_icono, cy - int(radio_icono/1.5)), 
                                            (cx + radio_icono, cy + int(radio_icono/1.5)), colorActual, 2)
                
                elif tipoFigura == "linea":
                    # Dibujar una pequeña línea diagonal
                    cv.line(combinado, (cx - radio_icono, cy + radio_icono), 
                                       (cx + radio_icono, cy - radio_icono), colorActual, 2)

    # Texto Info
    accion_texto = "ESPERANDO 'S'" if (modo == "figura" and puntoInicioFigura is None) else "CONTROLANDO"
    if modo == "pintar": accion_texto = "TRAZANDO"
    
    info_texto = f"MODO: {modo.upper()} | FIGURA: {tipoFigura.upper()} | ESTADO: {accion_texto}"
    cv.putText(combinado, info_texto, (10, alto - 20), cv.FONT_HERSHEY_SIMPLEX, 0.6, blanco, 2)

    cv.imshow("Pizarra Virtual", combinado)

    # 4. CONTROLES
    tecla = cv.waitKey(1) & 0xFF

    if tecla == 27: break
    elif tecla == ord('c'):
        lienzo = np.zeros_like(cuadro)
        puntoInicioFigura = None
    elif tecla == ord('m'):
        modo = "figura" if modo == "pintar" else "pintar"
        puntoInicioFigura = None
    elif tecla == ord('f'):
        if modo == "figura":
            if tipoFigura == "circulo": tipoFigura = "rectangulo"
            elif tipoFigura == "rectangulo": tipoFigura = "linea"
            else: tipoFigura = "circulo"
    elif tecla == ord('s'):
        if modo == "figura" and punto_actual is not None:
            puntoInicioFigura = punto_actual
    elif tecla == ord('e') or tecla == 32: 
        if modo == "figura" and figura_datos_actuales is not None and puntoInicioFigura is not None:
            d = figura_datos_actuales
            if d['tipo'] == 'circulo':
                cv.circle(lienzo, d['c'], d['r'], d['col'], 2)
            elif d['tipo'] == 'rectangulo':
                cv.drawContours(lienzo, [d['box']], 0, d['col'], 2)
            elif d['tipo'] == 'linea':
                cv.line(lienzo, d['p1'], d['p2'], d['col'], 5)
            
            puntoInicioFigura = None
            figura_datos_actuales = None

camara.release()
cv.destroyAllWindows()
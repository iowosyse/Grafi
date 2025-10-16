#2025-10-16
#Escalar un rectangulo según la distancia entre los dedos índices de las manos
import cv2 as cv
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Captura de video en tiempo real
cap = cv.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv.flip(frame, 1)
    h, w, _ = frame.shape
    # Convertir a RGB
    frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

    # Procesar la imagen con MediaPipe
    results = hands.process(frame_rgb)

    # Dibujar puntos de la mano y reconocer letras
    if results.multi_hand_landmarks and len(results.multi_hand_landmarks) == 2:
        for hand_landmarks in results.multi_hand_landmarks:
            manoIzqLandmarks = results.multi_hand_landmarks[0]
            manoDerLandmarks = results.multi_hand_landmarks[1]
            
            mp_drawing.draw_landmarks(frame, manoIzqLandmarks, mp_hands.HAND_CONNECTIONS)
            mp_drawing.draw_landmarks(frame, manoDerLandmarks, mp_hands.HAND_CONNECTIONS)
            # Obtener las coordenadas de los dedos índices
            puntaIdxIzq = manoIzqLandmarks.landmark[8]
            puntaIdxDer = manoDerLandmarks.landmark[8]
                
            xi = int(puntaIdxIzq.x * w)
            yi = int(puntaIdxIzq.y * h)    
            xd = int(puntaIdxDer.x * w)
            yd = int(puntaIdxDer.y * h)
                
            cv.rectangle(frame, (xi, yi), (xd, yd), (74, 89, 33), -1)
                       
    # Mostrar el video
    cv.imshow("Escalado de primitivas", frame)

    # Salir con la tecla 'q'
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar recursos
cap.release()
cv.destroyAllWindows()
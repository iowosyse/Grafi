# 2025-10-20
# Calculadora con UI relativa y detección por Labels (Izquierda=Pointer, Derecha=Click)
import cv2 as cv
import mediapipe as mp
import numpy as np

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7)

cap = cv.VideoCapture(0)
font = cv.FONT_HERSHEY_SIMPLEX

operation_string = "" 
action_locked = False 
current_selection = None 

#Definición de botones y pantalla (relativos)
buttons = {
    '7': (0.1, 0.25, 0.2, 0.35), '8': (0.25, 0.25, 0.35, 0.35), '9': (0.4, 0.25, 0.5, 0.35), '/': (0.55, 0.25, 0.65, 0.35),
    '4': (0.1, 0.4, 0.2, 0.5),   '5': (0.25, 0.4, 0.35, 0.5),   '6': (0.4, 0.4, 0.5, 0.5),   '*': (0.55, 0.4, 0.65, 0.5),
    '1': (0.1, 0.55, 0.2, 0.65), '2': (0.25, 0.55, 0.35, 0.65), '3': (0.4, 0.55, 0.5, 0.65), '-': (0.55, 0.55, 0.65, 0.65),
    'C': (0.1, 0.7, 0.2, 0.8),   '0': (0.25, 0.7, 0.35, 0.8),   '=': (0.4, 0.7, 0.5, 0.8),   '+': (0.55, 0.7, 0.65, 0.8),
}
screen_rect = (0.1, 0.1, 0.65, 0.2)

#Dibujar la calculadora
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

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv.flip(frame, 1)
    h, w, _ = frame.shape 
    frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    
    results = hands.process(frame_rgb)
    
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
        
    draw_calculator(frame, current_selection, w, h)
    cv.imshow("Calculadora con Manos", frame)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()

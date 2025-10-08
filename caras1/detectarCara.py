# 2025-10-03
# Detección de caras con OpenCV y dibujo de elementos gráficos sobre el rostro detectado
import cv2 as cv 

rostroCascade = cv.CascadeClassifier('C:\\Users\\cande\\OneDrive\\Escritorio\\Tec uwu\\Grafi\\Trabajos\\caras1\\haarcascade_frontalface_alt.xml')
cap = cv.VideoCapture(0)

while True:
    ret, img = cap.read()
    gris = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    rostros = rostroCascade.detectMultiScale(gris, 1.3, 5)
    for(x,y,w,h) in rostros:
        res = int((w+h)/8)
        anchoNariz = int(w/5)
        altoNariz = int(h/3)
        
        extra = w * 0.1

        y_sombrero_top = y - int(h * 0.4)
        x_sombrero_left = x + int(w * 0.2)
        ancho_sombrero = int(w * 0.6)
        
        #rectangulo azul
        img = cv.rectangle(img, (x,y), (x+w, y+h), (234, 23,23), 5)
        #rectangulo verde
        img = cv.rectangle(img, (x,int(y+h/2)), (x+w, y+h), (0,255,0),5 )
        #circulos negros
        img = cv.circle(img, (x + int(w*0.3), y + int(h*0.4)) , 21, (0, 0, 0), 2 )
        img = cv.circle(img, (x + int(w*0.7), y + int(h*0.4)) , 21, (0, 0, 0), 2 )
        #circulos blancos
        img = cv.circle(img, (x + int(w*0.3), y + int(h*0.4)) , 20, (255, 255, 255), -1 )
        img = cv.circle(img, (x + int(w*0.7), y + int(h*0.4)) , 20, (255, 255, 255), -1 )
        #pupilas rojas
        img = cv.circle(img, (x + int(w*0.3), y + int(h*0.4)) , 5, (0, 0, 255), -1 )
        img = cv.circle(img, (x + int(w*0.7), y + int(h*0.4)) , 5, (0, 0, 255), -1 )
        #nariz
        img = cv.rectangle( img, (x + 2 * anchoNariz, y + altoNariz), (x + anchoNariz * 3, y + altoNariz * 2), (255,0,255), 2)
        #boca
        img = cv.rectangle(img, (x + int(w/3.5), y + int(h*0.7)), (x + int(w*0.7), y + int(h*0.85  )), (255,255,0), 2)
        
        

    cv.imshow('img', img)
    if cv.waitKey(2) & 0xFF == 27:
        break
    
cap.release
cv.destroyAllWindows()
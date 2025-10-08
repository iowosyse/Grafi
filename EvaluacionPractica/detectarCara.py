# 2025-10-08
# Evaluación práctica
import cv2 as cv 

rostroCascade = cv.CascadeClassifier('EvaluacionPractica\\haarcascade_frontalface_alt.xml')
cap = cv.VideoCapture(0)

#variables para control de animaciones
#ojos
modificadorOjos = 0
vueltaOjos = 1
#lengua
modificadorLengua = 0
vueltaLengua = 1

while True:
    ret, img = cap.read()
    gris = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    rostros = rostroCascade.detectMultiScale(gris, 1.3, 5)
    for(x,y,w,h) in rostros:
        #proporciones para la nariz
        anchoNariz = int(w/5)
        altoNariz = int(h/3)
        
        #proporciones para los ojos
        radioBordeOjo = int(w * 0.08)
        radioGloboOcular = int(w * 0.075)
        radioPupila = int(w * 0.025)
        limiteOjo = radioGloboOcular - radioPupila
        
        #proporciones para la lengua
        yBoca = y + int(h*0.79)
        inicialLengua = y + int(h*0.85)
        maximoLengua = int (h * 0.12)
        
        #propporciones para las orejas
        centroOrejaIzq = (x + int(w * 0.05), y + int(h * 0.5))
        centroOrejaDer = (x + int(w * 0.95), y + int(h * 0.5))
        
        # posiciones para el sombrero
        yInfSombrero = y - int(h * 0.15)
        ySupSombrero = y - int(h * 0.6)
        
        # cuerpo del sombrero
        cv.rectangle(img, (x + int(w * 0.2), ySupSombrero), (x + int(w * 0.8), yInfSombrero), (0, 0, 0), -1)
        # ala del sombrero
        cv.rectangle( img, (x - int(w * 0.1), yInfSombrero), (x + int(w * 1.1), yInfSombrero - int(h * 0.05)), (0, 0, 0), -1)
        # liston del sombrero
        cv.rectangle(img, (x + int(w * 0.2), yInfSombrero - int(h * 0.1)), (x + int(w * 0.8), yInfSombrero - int(h * 0.05)), (10, 0, 255), -1)
        #rectangulo azul
        img = cv.rectangle(img, (x,y), (x+w, y+h), (234, 23,23), 5)
        #rectangulo verde
        img = cv.rectangle(img, (x,int(y+h/2)), (x+w, y+h), (0,255,0),5)
        #orejas
        cv.ellipse(img, centroOrejaIzq, (int(w * 0.1), int(h * 0.15)), 0, 0, 360, (80, 222, 249), 2)
        cv.ellipse(img, centroOrejaDer, (int(w * 0.1), int(h * 0.15)), 0, 0, 360, (80, 222, 249), 2)
        #circulos negros
        img = cv.circle(img, (x + int(w*0.3), y + int(h*0.4)) , radioBordeOjo, (0, 0, 0), 2 )
        img = cv.circle(img, (x + int(w*0.7), y + int(h*0.4)) , radioBordeOjo, (0, 0, 0), 2 )
        #circulos blancos
        img = cv.circle(img, (x + int(w*0.3), y + int(h*0.4)) , radioGloboOcular, (255, 255, 255), -1 )
        img = cv.circle(img, (x + int(w*0.7), y + int(h*0.4)) , radioGloboOcular, (255, 255, 255), -1 )
        #pupilas rojas
        img = cv.circle(img, (x + int(w*0.3) + modificadorOjos, y + int(h*0.4)) , radioPupila, (0, 0, 255), -1 )
        img = cv.circle(img, (x + int(w*0.7) + modificadorOjos, y + int(h*0.4)) , radioPupila, (0, 0, 255), -1 )
        #mover los ojos hacia los lados
        if vueltaOjos > 0:
            modificadorOjos += 1
            if modificadorOjos > limiteOjo:
                vueltaOjos *= -1
        else :
            modificadorOjos -= 1
            if modificadorOjos < -limiteOjo:
                vueltaOjos *= -1
        
        #rectangulo boca
        #img = cv.rectangle(img, (x + int(w/3.5), y + int(h*0.7)), (x + int(w*0.7), y + int(h*0.85  )), (255,255,0), 2)
        
        #circulo boca
        img = cv.circle(img, (x + int(2.5*anchoNariz), yBoca) , int(w*0.10), (0,0,0), -1 )
        #rectangulo nariz
        img = cv.rectangle(img, (x + 2 * anchoNariz, y + altoNariz), (x + anchoNariz * 3, y + altoNariz * 2), (255,0,255), 2)
        #rectangulo lengua
        img = cv.rectangle(img, (x + int (2.25 * anchoNariz), y + int(h*0.79)), (x + int(2.75 * anchoNariz), inicialLengua + modificadorLengua), (0,0,255), -1)
        #sacar la lengua
        if vueltaLengua  > 0:
            modificadorLengua += 2
            if modificadorLengua > maximoLengua:
                vueltaLengua *= -1
        #meter la lengua
        else :
            modificadorLengua -= 2
            if modificadorLengua < 0:
                vueltaLengua *= -1
            

    cv.imshow('img', img)
    if cv.waitKey(2) & 0xFF == 27:
        break
    
cap.release()
cv.destroyAllWindows()
import cv2
import random
from joystick import MandoGestos 
from ventanaJuego import VentanaJuego
import math
from enemigo import Enemy

VENTANAcAMARA = "Camara (debug)"


def principal():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("No se pudo abrir la cámara.")
        return

    mando = MandoGestos(radioZonaMuerta=80, cuadrosSostenidos=6, esperaSeleccion=1.2)
    juego = VentanaJuego()
    # el juego inicia el en menu
    estado = "MENU" 
    salir = 0
    i = 0
    
    
    # Agregamos cv2.WINDOW_NORMAL para permitir cambiar el tamaño
    cv2.namedWindow(VENTANAcAMARA, cv2.WINDOW_NORMAL)
    cv2.namedWindow(juego.nombreVentana)
                        
    # Definir el nuevo tamaño de la cámara (por ejemplo: Ancho 400, Alto 300)
    #cv2.resizeWindow(VENTANAcAMARA, 500, 350)
                                    
    # Mover las ventanas
    cv2.moveWindow(juego.nombreVentana, 600, 0)
    cv2.moveWindow(VENTANAcAMARA, 0, 0)
    
    while True:
        exito, cuadroCam = cap.read()
        if not exito:
            break
        cuadroCam = cv2.flip(cuadroCam, 1)

        datos, cuadroCam = mando.procesar(cuadroCam)

        # funciones del joystick
        if datos["seleccionado"] and estado == "STATS":
            if datos["direccion"] == "abajo":
                estado = "MENU"
            if datos["direccion"] == "derecha":
                juego.avatar.subirNivel()
            if datos["direccion"] == "izquierda":
                juego.avatar.vida = juego.avatar.vidaMax

        if datos["seleccionado"] and estado == "MENU":
            print(f"Accion confirmada: {datos['seleccionado']}")
            if datos["direccion"] == "arriba":
                estado = "MAPA1"
                i = 0
            if datos["direccion"] == "izquierda":
                estado = "STATS"
                i = 0
            if datos["direccion"] == "derecha":
                estado = "PELEA"
                enemigo1 = Enemy("assets/ruso.png", 950, 200, 220, 220, "Ruso", math.ceil(random.random()*5))
                mensaje = "sas"
                if(juego.avatar.vel >= enemigo1.vel):
                    subEstado = "TT"
                    sig = "TE"
                else:
                    subEstado = "TE"
                    sig = "TT"
                vidaJMax = juego.avatar.vidaMax
                vidaEMax = enemigo1.vida
                i = 0

            if datos["direccion"] == "abajo":                
                i += 1
                if i == 2:
                    break

        if datos["seleccionado"] and estado == "MAPA1":
            juego.avatar.mover(datos["direccion"], datos["seleccionado"], velocidad = juego.avatar.vel)
            if datos["seleccionado"] and datos["direccion"] == "abajo":
                estado = "MENU"

        if datos["seleccionado"] and estado == "PELEA":
            if datos["direccion"] == "abajo":
                estado = "MENU"
            if (subEstado == "G" or subEstado == "P") and datos["direccion"] == "arriba":
                estado = "MENU"


        #saltos de estado
        if estado == "MENU":
            lienzoJuego = juego.renderizarMenu(direccion=datos["direccion"], seleccionado=datos["seleccionado"])
        elif estado == "MAPA1":
            lienzoJuego = juego.renderizarMapa1(direccion=datos["direccion"], seleccionado=datos["seleccionado"])
        elif estado == "PELEA": 
            lienzoJuego, subEstado, sig, mensaje = juego.renderizarPelea(enemigo1, subEstado, sig, mensaje, vidaJMax, vidaEMax, direccion=datos["direccion"], seleccionado=datos["seleccionado"])
        elif estado == "STATS":
            lienzoJuego = juego.renderizarStats(direccion=datos["direccion"], seleccionado=datos["seleccionado"])
        else:
            lienzoJuego = juego.renderizar(direccion=datos["direccion"], seleccionado=datos["seleccionado"])

        juego.mostrar(lienzoJuego)
        cv2.imshow(VENTANAcAMARA, cuadroCam)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break

    mando.cerrar()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    principal()


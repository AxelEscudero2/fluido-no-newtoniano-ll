import cv2
import numpy as np
import random
from jugador import Jugador

class VentanaJuego:
    def __init__(self, ancho=1280, alto=720, nombreVentana="Fluido no Newtoniano II"):
        self.ancho = ancho
        self.alto = alto
        self.nombreVentana = nombreVentana
        self.fondo = cv2.imread("assets/fondo.png")
        self.fondo2 = cv2.imread("assets/fondo2.png")
        self.fondo3 = cv2.imread("assets/fondo3.png")
        self.fondo4 = cv2.imread("assets/fondo4.png")

        self.avatar = Jugador("assets/fnn.png", 640, 360, 110, 110)
        

    def renderizar(self, direccion="centro", seleccionado=None):

        lienzo = np.zeros((self.alto, self.ancho, 3), dtype=np.uint8)
        return lienzo
    
    def renderizarMenu(self, direccion, seleccionado):
        lienzo = self.fondo.copy()
        #sas meter webadas
        return lienzo

    def renderizarMapa1(self, direccion, seleccionado):
        
        self.avatar.mover(direccion, seleccionado, velocidad = self.avatar.vel)
        
        lienzo = self.fondo2.copy()
        self.avatar.dibujar(lienzo)
        return lienzo

    def renderizarStats(self, direccion, seleccionado):
        lienzo = self.fondo3.copy()
        
        fuente = cv2.FONT_HERSHEY_SIMPLEX
        escala = 0.9
        grosor = 2
        tipol = cv2.LINE_AA
       
        cv2.putText(lienzo, "Issac, el no newtoniano", (480, 150), fuente, escala, (10, 5, 255), grosor, tipol)
        cv2.putText(lienzo, f"Nivel: {self.avatar.nvl}", (80, 160), fuente, 1.4, (0, 0, 0), grosor, tipol)
        cv2.putText(lienzo, f"Ataque: {self.avatar.atk}", (80, 210), fuente, escala, (10, 5, 255), grosor, tipol)
        cv2.putText(lienzo, f"Vida: {self.avatar.vida}/{self.avatar.vidaMax}", (80, 260), fuente, escala, (10, 5, 255), grosor, tipol)
        cv2.putText(lienzo, f"Estado: {self.avatar.estado}", (80, 310), fuente, escala, (10, 5, 255), grosor, tipol)
        cv2.putText(lienzo, f"inteligencia: {self.avatar.intel}", (80, 360), fuente, escala, (10, 5, 255), grosor, tipol)
        cv2.putText(lienzo, f"Velocidad: {self.avatar.vel}", (80, 410), fuente, escala, (10, 5, 255), grosor, tipol)

        cv2.putText(lienzo, f"Exp: {self.avatar.exp}/{self.avatar.sigNvl}", (80, 590), fuente, escala, (10, 5, 255), grosor, tipol)
        
        Jugador("assets/fnn.png", 490, 240, 300, 300).dibujar(lienzo)
        
        return lienzo

    def _dibujarTexto(self, lienzo, texto, x, y, fuente, escala, color, grosor, tipoLinea, interlineado=35):
        for i, linea in enumerate(texto.split("\n")):
            cv2.putText(lienzo, linea, (x, y + i * interlineado), fuente, escala, color, grosor, tipoLinea)

    def renderizarPelea(self, enemigo, subEstado, sig, mensaje, vidaJMax, vidaEMax, direccion, seleccionado):
        lienzo = self.fondo4.copy()
        enemigo.dibujar(lienzo)
        Jugador("assets/fnn.png", 200, 200, 200, 200).dibujar(lienzo)
        
        fuente = cv2.FONT_HERSHEY_SIMPLEX
        escala = 0.9
        grosor = 2
        tipol = cv2.LINE_AA
        
        #los subestados indican en que parte del combate estas: TT es tu turno, TE es turno enemigo, R es resolucion, G es ganaste y P es perdiste
    
        

        if subEstado == "TT":
            sig = "TE"
            if not seleccionado and direccion == "arriba":
                mensaje = "golpe no newtoniano: lento pero seguro"

            if seleccionado and direccion == "arriba":
                damageHecho = round(self.avatar.ataque1(), 2)
                enemigo.vida -= damageHecho
                mensaje = f"has golpeado al ruso\ntendrás que lavarte las manos\nhas hecho {damageHecho} puntos de impacto\n(sube la mano y abre la palma para continuar)"
                subEstado = "R"
                if enemigo.vida <= 0:
                    sig = "G"

            if not seleccionado and direccion == "izquierda":
                mensaje = "patada no newtoniana: fuerte pero arriesgada"
            
            elif seleccionado and direccion == "izquierda":
                damageHecho = round(self.avatar.ataque2(), 2)
                enemigo.vida -= damageHecho
                
                mensaje = f"has pateado al ruso,\nespero que tengas buenos zapatos\nhas hecho {damageHecho} puntos de impacto\n(sube la mano y abre la palma para continuar)"
                subEstado = "R"
                if enemigo.vida <= 0:
                    sig = "G"

            if not seleccionado and direccion == "abajo":
                mensaje =  "salir al menu principal :("
        
            if not seleccionado and direccion == "derecha":
                mensaje = "issac, el cree que puede ganar, \neso le dijo su mama"
            if not seleccionado and direccion == "centro":
                mensaje = "pon la mano sobre una opcion para leer\nlo que puede hacer"
                
        

        elif subEstado == "TE":
            sig = "TT"
            if random.random() > 0.6:
                damageRecibido = round(enemigo.ataque2(), 2)
                self.avatar.vida -= damageRecibido
                mensaje = f"te han tacleado \nhas recibido {damageRecibido} puntos de impacto\n(sube la mano y abre la palma para continuar)"
                subEstado = "R"
                if self.avatar.vida <= 0:
                    sig = "P"
            else:
                damageRecibido = round(enemigo.ataque1(), 2)
                self.avatar.vida -= damageRecibido
                mensaje = f"te acaban de golpear\nhas recibido {damageRecibido} puntos de impacto\n(sube la mano y abre la palma para continuar)"
                subEstado = "R"
                if self.avatar.vida <= 0:
                    sig = "P"


        elif subEstado == "R":
                        
            if seleccionado and direccion == "arriba":
                subEstado = sig
        elif subEstado == "G":
            mensaje = "acabaste con el Ruso, \nestas un paso mas cerca de disolver la union sovietica, \nfelicidades\n(sube la mano y abre la palma para continuar)"
            subEstado = "R"
        elif subEstado == "P":        
            mensaje = "perdiste, caiste inconsciente\n(sube la mano y abre la palma para continuar)"
            subEstado = "R"
        
        self._dibujarTexto(lienzo, mensaje, 450, 550, fuente, escala, (10, 5, 255), grosor, tipol)
        cv2.putText(lienzo, f"{round(self.avatar.vida, 2)}/{vidaJMax}", (205, 150), fuente, escala, (10, 5, 255), grosor, tipol)
        cv2.putText(lienzo, f"{round(enemigo.vida, 2)}/{vidaEMax}", (965, 150), fuente, escala, (10, 5, 255), grosor, tipol)
        
        cv2.putText(lienzo, f"Nvl{enemigo.nvl} Ruso, Petricov", (950, 100), fuente, escala, (10, 5, 255), grosor, tipol)
        cv2.putText(lienzo, f"Nvl{self.avatar.nvl} Issac, el no newtoniano", (200, 100), fuente, escala, (10, 5, 255), grosor, tipol)

        return lienzo, subEstado, sig, mensaje

    def mostrar(self, lienzo):
        cv2.imshow(self.nombreVentana, lienzo)

import cv2
import random

class Jugador:
    def __init__(self, ruta_sprite, x_inicial, y_inicial, ancho, alto):
        self.x = x_inicial
        self.y = y_inicial
        self.an = ancho
        self.al = alto
        self.skin = ruta_sprite

        self.atk = 20
        self.vida = 100
        self.vidaMax = 100
        self.estado = 20
        self.nvl = 1
        self.intel = 20
        self.vel = 10
        self.exp = 0
        self.sigNvl = 10
                                                    
        # Cargamos el sprite con su canal alfa (transparencia)
        img = cv2.imread(ruta_sprite, cv2.IMREAD_UNCHANGED)
        if img is not None:
            self.sprite = cv2.resize(img, (ancho, alto))
        else:
            print(f"Error: No se pudo cargar el sprite {ruta_sprite}")
            self.sprite = None

    def mover(self, direccion, seleccionado, velocidad=10):
        
        if direccion == "derecha":
            self.x += velocidad
        elif direccion == "izquierda":
            self.x -= velocidad
        elif direccion == "arriba":
            self.y -= velocidad
        elif direccion == "abajo":
            self.y += velocidad

    def dibujar(self, lienzo):
        h, w, c = self.sprite.shape
        # Límites de la pantalla para evitar errores de recorte (slicing)
        y1, y2 = max(0, self.y), min(lienzo.shape[0], self.y + h)
        x1, x2 = max(0, self.x), min(lienzo.shape[1], self.x + w)
                                                                                                                                                                                                                                                                                                                                            
        sprite_y1, sprite_y2 = y1 - self.y, y2 - self.y
        sprite_x1, sprite_x2 = x1 - self.x, x2 - self.x

        if x2 <= x1 or y2 <= y1:#para que no explote al salir del los limites del mapa xd
            return

        if c == 4: # aqui dibuja
            alpha = self.sprite[sprite_y1:sprite_y2, sprite_x1:sprite_x2, 3] / 255.0
            for ch in range(3):
                lienzo[y1:y2, x1:x2, ch] = (alpha * self.sprite[sprite_y1:sprite_y2, sprite_x1:sprite_x2, ch] + (1 - alpha) * lienzo[y1:y2, x1:x2, ch])
        

    def subirNivel(self):
        self.atk = round(self.atk * 1.2, 2)
        self.vida += 25
        self.vidaMax += 25
        self.estado = round(self.estado * 1.2, 2)
        self.nvl += 1
        self.intel = round(self.intel * 1.2, 2)
        self.vel += 5
        self.exp -= self.sigNvl
        self.sigNvl = round(self.sigNvl * 1.2, 2)

    def ataque1(self):
        if random.random() > 0.85:
            return self.atk * 1.5
        return self.atk

    def ataque2(self):
        if random.random() > 0.5:
            return self.atk * 2.5
        return self.atk * 0.8

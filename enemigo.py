import cv2
import numpy
import random

class Enemy:
    def __init__(self, ruta_sprite, xi, yi, ancho, alto, nombre, nvl):
        self.x = xi
        self.y = yi
        self.an = ancho
        self.al = alto
        self.skin = ruta_sprite

        self.atk = round(12 * (1.2 ** nvl), 2)
        self.vida = 90 + 20 * nvl
        self.estado = round(20 * (1.2 ** nvl), 2)
        self.intel = round(25 * (1.1 ** nvl), 2)
        self.vel = 8 + 5 * nvl
        self.nvl = nvl

    def ataque1(self):
        if random.random() > 0.85:
            return self.atk * 1.5
        return self.atk

    def ataque2(self):
        if random.random() > 0.5:
            return self.atk * 2.5
        return self.atk * 0.75
    
    def dibujar(self, lienzo):
        sprite = cv2.resize(cv2.imread(self.skin, cv2.IMREAD_UNCHANGED), (self.an, self.al))
        h, w, c = sprite.shape
        
        # Límites de la pantalla para evitar errores de recorte (slicing)
        y1, y2 = max(0, self.y), min(lienzo.shape[0], self.y + h)
        x1, x2 = max(0, self.x), min(lienzo.shape[1], self.x + w)

        sprite_y1, sprite_y2 = y1 - self.y, y2 - self.y
        sprite_x1, sprite_x2 = x1 - self.x, x2 - self.x

        if x2 <= x1 or y2 <= y1:#para que no explote al salir del los limites del mapa xd
            return

        if c == 4: # aqui dibuja
            alpha = sprite[sprite_y1:sprite_y2, sprite_x1:sprite_x2, 3] / 255.0
            for ch in range(3):
                lienzo[y1:y2, x1:x2, ch] = (alpha * sprite[sprite_y1:sprite_y2, sprite_x1:sprite_x2, ch] + (1 - alpha) * lienzo[y1:y2, x1:x2, ch])

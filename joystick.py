"""
mandoGestos.py
--------------
Convierte cámara + MediaPipe en un "mando" (joystick) controlado por gestos:

- La posición de la CABEZA es el centro relativo (origen del mando).
- La posición de la MANO (puño cerrado) respecto a la cabeza define una
  dirección: arriba / abajo / izquierda / derecha / centro.
- Al ABRIR la palma mientras se sostiene una dirección estable, se dispara
  un evento de "selección" (equivalente al botón A de un joystick).

Uso típico dentro de un juego:

    mando = MandoGestos()
    while True:
        exito, cuadro = cap.read()
        datos, cuadro = mando.procesar(cuadro)
        # datos["direccion"]    -> "arriba" | "abajo" | "izquierda" | "derecha" | "centro"
        # datos["seleccionado"] -> None o la dirección que se acaba de confirmar
        cv2.imshow("ventana", cuadro)
"""

import math
import time

import cv2

# NOTA: en algunas versiones/instalaciones recientes de mediapipe,
# `mediapipe.solutions` no se expone bien como atributo del paquete
# (bug conocido, ver github.com/google-ai-edge/mediapipe/issues/6200 y 6204).
# Por eso importamos los submódulos directamente, que es más confiable.
try:
    from mediapipe.python.solutions import hands as moduloManos
    from mediapipe.python.solutions import face_detection as moduloCara
    from mediapipe.python.solutions import drawing_utils as moduloDibujo
except ImportError:
    import mediapipe as mp  # "mp" se deja así: es el alias universal de la librería
    moduloManos = mp.solutions.hands
    moduloCara = mp.solutions.face_detection
    moduloDibujo = mp.solutions.drawing_utils

        """
        radioZonaMuerta  : radio (px) alrededor del ANCLA donde la mano
                            todavía cuenta como "centro" (evita ruido cuando
                            la mano está muy cerca de la cara).
        cuadrosSostenidos: cuántos cuadros seguidos debe mantenerse la misma
                            dirección para considerarla "estable".
        esperaSeleccion  : segundos mínimos entre dos selecciones seguidas.
        maxManos         : máximo de manos a detectar a la vez.
        margenDedo       : qué tan "estirado" debe estar un dedo para
                            contarlo como extendido (ajustar si detecta mal).
        radioAnclaCabeza : radio (px) que la cabeza debe recorrer para que
                            el "origen" del mando se recalcule. Mientras la
                            cabeza se mueva dentro de ese radio, el ancla se
                            queda fija (evita jitter). Si no se especifica,
                            usa el mismo valor que radioZonaMuerta.
        
        """
class MandoGestos:
    def __init__(self, radioZonaMuerta=80, cuadrosSostenidos=6, esperaSeleccion=1.0, maxManos=1, margenDedo=1.15, radioAnclaCabeza=None):
        
        self.m = moduloManos     # referencia al submódulo "hands" de mediapipe
        self.c = moduloCara      # referencia al submódulo "face_detection"
        self.dib = moduloDibujo  # referencia al submódulo "drawing_utils"

        # Ojo: max_num_hands, min_detection_confidence, etc. son nombres de
        # parámetro FIJOS por mediapipe (así los definió su función Hands()).
        # No se pueden renombrar, aunque el valor que les pasamos sí sea
        # una variable nuestra (maxManos).
        
        self.manos = self.m.Hands(
            static_image_mode=False, 
            max_num_hands=maxManos, 
            min_detection_confidence=0.7, 
            min_tracking_confidence=0.6,
            )

        self.cara = self.c.FaceDetection(
            model_selection=0, min_detection_confidence=0.6
        )

        self.radioZonaMuerta = radioZonaMuerta
        self.cSostenidos = cuadrosSostenidos
        self.espera = esperaSeleccion
        self.margenDedo = margenDedo
        self.rEstaca = (
            radioAnclaCabeza if radioAnclaCabeza is not None else radioZonaMuerta
        )

        self._historial = []
        self._ultimoEstado = "cerrada"  # cerrada = puño, abierta = palma
        self._ultimaHora = 0.0
        self._estaca = None  # (x, y) fija: el "origen" del mando

    

    def _centroCabeza(self, resultadosCara, ancho, alto):
        if not resultadosCara.detections:
            return None
        det = resultadosCara.detections[0]
        caja = det.location_data.relative_bounding_box
        cx = (caja.xmin + caja.width / 2) * ancho
        cy = (caja.ymin + caja.height / 2) * alto
        return (cx, cy)

    def _dedoExtendido(self, landmarks, idxPunta, idxNudillo, idxMuneca=0):
        muneca = landmarks[idxMuneca]
        punta = landmarks[idxPunta]
        nudillo = landmarks[idxNudillo]
        distPunta = math.hypot(punta.x - muneca.x, punta.y - muneca.y)
        distNudillo = math.hypot(nudillo.x - muneca.x, nudillo.y - muneca.y)
        return distPunta > distNudillo * self.margenDedo

    def _clasificarMano(self, landmarks):
        # (punta, nudillo) de índice, medio, anular, meñique
        dedos = [(8, 6), (12, 10), (16, 14), (20, 18)]
        conteoExtendidos = sum(
            self._dedoExtendido(landmarks, punta, nudillo) for punta, nudillo in dedos
        )
        if conteoExtendidos >= 3:
            return "abierta"
        elif conteoExtendidos <= 1:
            return "cerrada"
        return "desconocida"

    def _centroMano(self, landmarks, ancho, alto):
        idxs = [0, 5, 9, 13, 17]  # muñeca + base de los 4 dedos largos
        xs = [landmarks[i].x * ancho for i in idxs]
        ys = [landmarks[i].y * alto for i in idxs]
        return (sum(xs) / len(xs), sum(ys) / len(ys))

    def _actualizarEstaca(self, centroCabezaCrudo):
        """
        Actualiza (o no) el ancla fija de la cabeza. Mientras el centro
        detectado se mantenga a menos de rEstaca de la estaca
        actual, el ancla NO se mueve. Solo "salta" a la nueva posición
        cuando te sales de ese radio. Así el origen del mando no
        tiembla con el ruido normal de la detección facial.
        """
        if centroCabezaCrudo is None:
            # no se detectó cara este cuadro: seguimos usando el ancla vieja
            return self._estaca

        if self._estaca is None:
            self._estaca = centroCabezaCrudo
            return self._estaca

        dx = centroCabezaCrudo[0] - self._estaca[0]
        dy = centroCabezaCrudo[1] - self._estaca[1]
        if math.hypot(dx, dy) > self.rEstaca:
            self._estaca = centroCabezaCrudo

        return self._estaca

    def _direccionDesdeVector(self, dx, dy):
        dist = math.hypot(dx, dy)
        if dist < self.radioZonaMuerta:
            return "centro"
        if abs(dx) > abs(dy):
            return "derecha" if dx > 0 else "izquierda"
        else:
            return "abajo" if dy > 0 else "arriba"

    





    def procesar(self, cuadro):
        """
        Procesa un cuadro de la cámara (BGR, como lo entrega OpenCV).
        Devuelve (datos, cuadro_anotado).
        """
        alto, ancho = cuadro.shape[:2]
        rgb = cv2.cvtColor(cuadro, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False

        resultadosManos = self.manos.process(rgb)
        resultadosCara = self.cara.process(rgb)

        rgb.flags.writeable = True

        datos = {
            "centroCabeza": None,
            "centroCabezaCrudo": None,
            "centroMano": None,
            "direccion": "sinDeteccion",
            "estadoMano": None,
            "seleccionado": None,
            "vectorMano": None,
        }

        centroCabezaCrudo = self._centroCabeza(resultadosCara, ancho, alto)
        centroCabeza = self._actualizarEstaca(centroCabezaCrudo)
        datos["centroCabeza"] = centroCabeza
        datos["centroCabezaCrudo"] = centroCabezaCrudo

        if centroCabeza and resultadosManos.multi_hand_landmarks:
            landmarks = resultadosManos.multi_hand_landmarks[0].landmark
            centroMano = self._centroMano(landmarks, ancho, alto)
            estadoMano = self._clasificarMano(landmarks)
            datos["centroMano"] = centroMano
            datos["estadoMano"] = estadoMano

            dx = centroMano[0] - centroCabeza[0]
            dy = centroMano[1] - centroCabeza[1]
            datos["vectorMano"] = (dx, dy)
            direccion = self._direccionDesdeVector(dx, dy)
            datos["direccion"] = direccion

            # historial para exigir dirección "estable"
            self._historial.append(direccion)
            if len(self._historial) > self.cSostenidos:
                self._historial.pop(0)

            direccionEstable = None
            if (
                len(self._historial) == self.cSostenidos
                and len(set(self._historial)) == 1
            ):
                direccionEstable = self._historial[0]

            ahora = time.time()
            if (estadoMano == "abierta"
                and self._ultimoEstado == "cerrada"
                and direccionEstable not in (None, "centro")
                and ahora - self._ultimaHora > self.espera
            ):
                datos["seleccionado"] = direccionEstable
                self._ultimaHora = ahora

            if estadoMano in ("abierta", "cerrada"):
                self._ultimoEstado = estadoMano

            self.dib.draw_landmarks(
                cuadro,
                resultadosManos.multi_hand_landmarks[0],
                self.m.HAND_CONNECTIONS,
            )

        if centroCabeza:
            # círculo del ancla (el origen fijo del mando)
            cv2.circle(cuadro,
                    (int(centroCabeza[0]), int(centroCabeza[1])),
                    self.radioZonaMuerta,
                    (255, 255, 0),
                    1,
            )
            cv2.circle(
                cuadro, (int(centroCabeza[0]), int(centroCabeza[1])), 5, (0, 255, 255), -1
            )
        if centroCabezaCrudo:
            # punto rojo pequeño: posición REAL detectada de la cara este
            # cuadro (solo debug, para ver cuánto se "resiste" el ancla)
            cv2.circle(
                cuadro,
                (int(centroCabezaCrudo[0]), int(centroCabezaCrudo[1])),
                3, (0, 0, 255), -1,
            )

        return datos, cuadro

    def cerrar(self):
        self.manos.close()
        self.cara.close()

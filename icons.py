# -*- coding: utf-8 -*-
"""
icons.py
Los iconos del diseno son SVG de trazo (stroke) en un lienzo de 24x24.
Kivy no lee SVG, asi que aqui cada icono se describe como una lista de
operaciones que luego se dibujan con kivy.graphics.Line.

Operaciones soportadas:
  ('pl', [(x, y), ...])         -> polilinea
  ('c',  cx, cy, r)             -> circulo
  ('r',  x, y, w, h, radio)     -> rectangulo redondeado
  ('a',  cx, cy, r, a0, a1)     -> arco (grados, sistema SVG: y crece hacia abajo)

Todas las coordenadas estan en el espacio 0..24 del SVG original.
"""
import math


def arc_points(cx, cy, r, a0, a1, steps=28):
    """Convierte un arco en una polilinea de puntos (espacio SVG)."""
    pts = []
    for i in range(steps + 1):
        ang = math.radians(a0 + (a1 - a0) * i / steps)
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return pts


ICONS = {
    # Pin de "Pedir Vacaciones"
    'vacation': [
        ('pl', arc_points(12, 7.5, 5.5, 180, 360) + [(12, 18.5), (6.5, 7.5)]),
        ('c', 12, 7.5, 1.75),
    ],
    # Cuadro con "+" de "Solicitar Permiso"
    'permit': [
        ('r', 4, 4, 16, 16, 3),
        ('pl', [(8, 12), (16, 12)]),
        ('pl', [(12, 8), (12, 16)]),
    ],
    # Camara de "Subir Licencia"
    'camera': [
        ('r', 1, 6, 22, 15, 3),
        ('pl', [(7, 6), (9, 3), (15, 3), (17, 6)]),
        ('c', 12, 13, 4),
    ],
    # Lapiz (firmar)
    'pen': [
        ('pl', [(11, 4), (5, 4), (4, 5), (4, 20), (5, 21), (19, 21), (20, 20), (20, 13)]),
        ('pl', [(18.5, 2.5), (21.5, 5.5), (12, 15), (8, 16), (9, 12), (18.5, 2.5)]),
    ],
    # Check (usado como "nube ok" y como confirmacion)
    'check': [
        ('pl', [(20, 6), (9, 17), (4, 12)]),
    ],
    # Pin pequeno "Fijados al dispositivo"
    'pin': [
        ('pl', arc_points(12, 10, 9, 180, 360) + [(12, 23), (3, 10)]),
        ('c', 12, 10, 3),
    ],
    # Flecha derecha
    'chevron': [
        ('pl', [(9, 18), (15, 12), (9, 6)]),
    ],
    # Campana de notificaciones
    'bell': [
        ('pl', arc_points(12, 8, 6, 180, 360)),
        ('pl', [(18, 8), (18, 12), (21, 17), (3, 17), (6, 12), (6, 8)]),
        ('pl', [(10.27, 19), (12, 20.3), (13.73, 19)]),
    ],
    # Documento
    'file': [
        ('pl', [(14, 2), (6, 2), (4, 4), (4, 20), (6, 22), (18, 22), (20, 20), (20, 8), (14, 2)]),
        ('pl', [(14, 2), (14, 8), (20, 8)]),
        ('pl', [(8, 13), (16, 13)]),
        ('pl', [(8, 17), (16, 17)]),
    ],
    # Cerrar (X)
    'close': [
        ('pl', [(18, 6), (6, 18)]),
        ('pl', [(6, 6), (18, 18)]),
    ],
    # Papelera
    'trash': [
        ('pl', [(3, 6), (21, 6)]),
        ('pl', [(19, 6), (18, 20), (6, 20), (5, 6)]),
        ('pl', [(10, 11), (10, 17)]),
        ('pl', [(14, 11), (14, 17)]),
        ('pl', [(9, 6), (9, 4), (15, 4), (15, 6)]),
    ],
    # Flecha izquierda (volver)
    'back': [
        ('pl', [(15, 18), (9, 12), (15, 6)]),
    ],
    # Flecha abajo (desplegable)
    'down': [
        ('pl', [(6, 9), (12, 15), (18, 9)]),
    ],
    # Calendario
    'calendar': [
        ('r', 3, 5, 18, 16, 3),
        ('pl', [(3, 10), (21, 10)]),
        ('pl', [(8, 3), (8, 7)]),
        ('pl', [(16, 3), (16, 7)]),
    ],
    # Subir archivo
    'upload': [
        ('pl', [(12, 16), (12, 4)]),
        ('pl', [(7, 9), (12, 4), (17, 9)]),
        ('pl', [(4, 16), (4, 20), (20, 20), (20, 16)]),
    ],
    # Reloj (solicitud pendiente)
    'clock': [
        ('c', 12, 12, 9),
        ('pl', [(12, 7), (12, 12), (16, 14)]),
    ],
    # Wifi
    'wifi': [
        ('pl', arc_points(12, 20, 12.6, 197, 343, 20)),
        ('pl', arc_points(12, 20, 9.1, 200, 340, 20)),
        ('pl', arc_points(12, 20, 5.3, 205, 335, 20)),
        ('pl', [(11.9, 20), (12.1, 20)]),
    ],
}

# Grosor del trazo de cada icono (igual al strokeWidth del SVG original)
STROKE = {
    'vacation': 1.8, 'permit': 1.8, 'camera': 1.8, 'pen': 1.8, 'check': 2.5,
    'pin': 1.8, 'chevron': 2.0, 'bell': 1.8, 'file': 1.8, 'close': 2.0,
    'trash': 1.8, 'wifi': 1.8, 'back': 2.2, 'down': 2.2, 'calendar': 1.8,
    'upload': 1.8, 'clock': 1.8,
}

# -*- coding: utf-8 -*-
"""
notifications.py
Notificaciones locales con Plyer -- Sesion 22, pilar "3. Notificaciones
(Plyer)". Plyer es una capa que llama a la API de notificaciones nativa de
cada plataforma (Windows, Android, Linux...) con el mismo codigo Python:
el proyecto no escribe nada especifico de Windows ni de Android, Plyer
elige el backend correcto en tiempo de ejecucion.

Son notificaciones LOCALES (las dispara la propia app en el dispositivo),
no notificaciones push de un servidor -- no hay backend de mensajeria en
esta maqueta. Encajan en el mismo lugar que llenaria una FCM/APNs real si
el proyecto creciera mas alla de esta entrega.

notify() nunca lanza una excepcion hacia quien la llama: si Plyer no esta
instalado, o el sistema operativo no tiene un backend de notificaciones
disponible (por ejemplo, este mismo entorno de pruebas sin pantalla), se
registra en el log y la app sigue funcionando igual -- una notificacion
fallida no deberia nunca tumbar la app ni interrumpir el flujo de firma.
"""
from kivy.logger import Logger

try:
    from plyer import notification as _notification
except Exception:  # Plyer no instalado, o sin backend para este SO
    _notification = None


def notify(title, message, timeout=6):
    """Muestra una notificacion del sistema operativo. Si falla por
    cualquier motivo, solo lo registra en el log -- no interrumpe la app."""
    if _notification is None:
        Logger.info('Notificaciones: Plyer no disponible, se omite "%s"', title)
        return
    try:
        _notification.notify(title=title, message=message, timeout=timeout,
                             app_name='FirmApp')
    except Exception as exc:  # NotImplementedError, backend sin configurar, etc.
        Logger.warning('Notificaciones: no se pudo mostrar "%s" (%s)', title, exc)

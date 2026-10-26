# -*- coding: utf-8 -*-
"""
remote_config.py
Configuracion remota (Remote Config) -- Sesion 22, pilar "4. Remote Config".

Patron cliente/servidor: la app SIEMPRE arranca con valores locales seguros
(Default Local) y, en paralelo, intenta traer un JSON desde internet con
kivy.network.urlrequest.UrlRequest (Fetch Asincrono -- no bloquea la
interfaz mientras espera la respuesta de la red). Si el servidor responde
con un JSON valido, esos valores reemplazan a los locales (Activate); si
falla, no hay conexion o la respuesta viene mal formada, la app se queda
con los valores locales sin interrumpir al usuario (Fallback). Ver la
diapositiva "Flujo Seguro y Resiliencia de Red" (nunca confiar en la red).

Este modulo no sabe nada de KivyMD ni de pantallas: solo pide un JSON y
entrega un dict ya fusionado con los valores por defecto. Quien lo usa
(main.py) decide que propiedades de la app actualizar con ese dict.
"""
import json

from kivy.network.urlrequest import UrlRequest
from kivy.logger import Logger

# Valores por defecto (Default Local): la app SIEMPRE puede arrancar con
# esto, incluso sin internet. El JSON remoto puede traer todas, algunas o
# ninguna de estas claves -- la que falte se queda con su valor local.
DEFAULTS = {
    # Texto corto opcional bajo el saludo del Dashboard (vacio = no se
    # muestra). Ejemplo del equipo docente: "banner": "Hola, Comunidad!".
    'banner_message': '',
    # Feature flag: enciende/apaga la tarjeta "Firmar sin sesion" sin
    # tener que recompilar ni reinstalar la app.
    'show_desktop_cta': False,
    # Limite numerico: cuantas "Liquidaciones Recientes" se listan.
    'max_recent_docs': 4,
}


def fetch(url, on_loaded, on_failed=None, timeout=6):
    """
    Pide el JSON remoto en segundo plano. No bloquea la interfaz: Kivy
    sigue dibujando y respondiendo a toques mientras se espera la red.

    on_loaded(dict): se llama SOLO si la respuesta llega y es un objeto
        JSON valido -- recibe DEFAULTS fusionado con lo que trajo el
        servidor (las claves que el servidor no mando quedan en su valor
        local).
    on_failed(): opcional. Se llama si no hay conexion, el servidor no
        responde o el JSON viene mal formado -- es decir, cuando toca
        quedarse con el Fallback local. Si no se pasa, simplemente no pasa
        nada (la app ya arranco con DEFAULTS, asi que no hace falta hacer
        nada mas para seguir funcionando).
    """
    def _aplicar(resultado):
        # UrlRequest solo decodifica el JSON solo si el servidor responde
        # con el header 'Content-Type: application/json'. GitHub (raw.
        # githubusercontent.com) sirve los .json como 'text/plain', asi que
        # aqui llega como texto plano -- se intenta decodificar a mano
        # antes de rendirse.
        if isinstance(resultado, (str, bytes)):
            try:
                resultado = json.loads(resultado)
            except ValueError:
                Logger.warning('RemoteConfig: la respuesta no es JSON valido '
                                '-- se ignora y se mantiene el valor local')
                if on_failed:
                    on_failed()
                return
        if not isinstance(resultado, dict):
            Logger.warning('RemoteConfig: la respuesta no es un objeto JSON '
                            '-- se ignora y se mantiene el valor local')
            if on_failed:
                on_failed()
            return
        fusionado = dict(DEFAULTS)
        fusionado.update(resultado)
        Logger.info('RemoteConfig: configuracion remota aplicada: %s', fusionado)
        on_loaded(fusionado)

    def _on_success(request, result):
        _aplicar(result)

    def _on_error(request, error):
        # Sin conexion, DNS caido, timeout, etc.
        Logger.warning('RemoteConfig: sin conexion (%s) -- se mantiene el '
                        'valor local (Fallback)', error)
        if on_failed:
            on_failed()

    def _on_failure(request, result):
        # El servidor respondio, pero con un error HTTP (404, 500...).
        Logger.warning('RemoteConfig: el servidor respondio con error -- '
                        'se mantiene el valor local (Fallback)')
        if on_failed:
            on_failed()

    UrlRequest(url, on_success=_on_success, on_error=_on_error,
               on_failure=_on_failure, timeout=timeout)

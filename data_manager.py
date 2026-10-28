# -*- coding: utf-8 -*-
"""
data_manager.py
Persistencia de datos en JSON -- Sesion 24 (Evaluacion N3), Criterio B
("Login validado y los datos criticos persisten entre ejecuciones (JSON),
manejando excepciones") y Check-in 2 de la diapositiva ("Los datos de la
comunidad no deben desaparecer al cerrar la app").

Guarda y recupera, en archivos JSON locales, los dos "datos criticos" de
FirmApp:
  - usuarios.json  -> cuentas registradas (RUT/correo + contrasena, con
                       hash -- ver LoginScreen/RegisterScreen en main.py).
  - documentos.json -> que documentos siguen PENDING y cuales ya pasaron
                       a RECENT (firmados), para que sobrevivan a cerrar
                       y volver a abrir la app.

Sin esto, cada reinicio de la app volveria siempre a los mismos datos de
ejemplo fijos en main.py (PENDING/RECENT), como si nunca se hubiera
firmado ni registrado nada -- igual que antes de este archivo.

Este modulo no sabe nada de Kivy: solo lee y escribe JSON en disco. Cada
operacion de E/S esta en su propio try/except (igual que el ejemplo de la
diapositiva "Check-in 2"): un error de disco nunca debe tumbar la app ni
interrumpir el flujo de firma -- en el peor caso, se pierde ese guardado
puntual y la app sigue funcionando con lo que ya tenia en memoria.
"""
import hashlib
import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(_HERE, 'data')
USERS_FILE = os.path.join(DATA_DIR, 'usuarios.json')
DOCS_FILE = os.path.join(DATA_DIR, 'documentos.json')
REQUESTS_FILE = os.path.join(DATA_DIR, 'solicitudes.json')
ADMIN_ID = 'admin@firmapp.cl'


def _hash_password(password):
    """Hash simple (SHA-256) para no guardar contrasenas en texto plano
    en el JSON. No es para produccion (faltaria sal por usuario, por
    ejemplo) -- alcanza para esta maqueta, y es mejor que texto plano."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def _normalize_key(identifier):
    """Clave canonica de una cuenta: el correo en minusculas, o el RUT solo
    con digitos y K mayuscula -- asi '12.345.678-5' y '123456785' son la
    misma cuenta (no se puede registrar dos veces en distinto formato)."""
    text = identifier.strip()
    if '@' in text:
        return text.lower()
    return ''.join(c for c in text if c.isdigit() or c in 'kK').upper()


class DataManager:
    """
    Agrupa toda la persistencia de la app. InterfazRRHHApp crea una sola
    instancia (self.dm) y la usa para:
      - validar login / registrar cuentas nuevas (usuarios.json)
      - guardar el estado de los documentos cada vez que se firma uno
        (documentos.json), y recuperarlo al abrir la app.
    """

    def __init__(self):
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
        except OSError as exc:
            print('DataManager: no se pudo crear la carpeta data/ (%s)' % exc)
        # Cuentas precargadas, para poder iniciar sesion sin registrarse antes
        # (el "Plan B Tecnico" de la Sesion 24 recomienda tener datos de
        # respaldo listos para la demo): un trabajador de prueba y la cuenta
        # de ADMINISTRADOR que crea los documentos por firmar. Se agregan solo
        # si faltan, asi tambien aparecen en un usuarios.json ya existente.
        users = self.load_users()
        seeded = False
        for key, password, role in (
                ('demo@firmapp.cl', 'demo1234', 'trabajador'),
                (ADMIN_ID, 'admin1234', 'admin')):
            if key not in users:
                users[key] = {'password_hash': _hash_password(password), 'role': role}
                seeded = True
        if seeded:
            self._save_users(users)

    # =============================================================== USUARIOS
    def load_users(self):
        """Devuelve el diccionario {identificador: {password_hash}} guardado,
        o {} si el archivo no existe todavia o esta corrupto."""
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except (IOError, OSError, json.JSONDecodeError) as exc:
            print('DataManager: no se pudo leer usuarios.json (%s) -- '
                  'se asume que no hay cuentas registradas' % exc)
            return {}

    def _save_users(self, users):
        try:
            with open(USERS_FILE, 'w', encoding='utf-8') as f:
                json.dump(users, f, indent=2, ensure_ascii=False)
            return True
        except (IOError, OSError) as exc:
            print('DataManager: no se pudo guardar usuarios.json (%s)' % exc)
            return False

    def register_user(self, identifier, password):
        """Crea una cuenta nueva. Devuelve (ok, mensaje) -- ok=False si ya
        existe una cuenta con ese identificador o si fallo el guardado."""
        key = _normalize_key(identifier)
        users = self.load_users()
        if key in users:
            return False, 'Ya existe una cuenta con ese RUT o correo.'
        users[key] = {'password_hash': _hash_password(password), 'role': 'trabajador'}
        if not self._save_users(users):
            return False, 'No se pudo guardar la cuenta (error de disco).'
        return True, 'Cuenta creada correctamente.'

    def authenticate(self, identifier, password):
        """True si el identificador y la contrasena coinciden con una
        cuenta registrada en usuarios.json."""
        key = _normalize_key(identifier)
        user = self.load_users().get(key)
        if not user:
            return False
        return user.get('password_hash') == _hash_password(password)

    def get_role(self, identifier):
        """'admin' o 'trabajador' (las cuentas registradas desde la app son
        siempre 'trabajador': solo se puede ser admin editando usuarios.json)."""
        user = self.load_users().get(_normalize_key(identifier), {})
        return user.get('role', 'trabajador')

    # ============================================================= DOCUMENTOS
    def load_documents(self, default_pending, default_recent):
        """Devuelve (pending, recent) guardados en documentos.json. Si el
        archivo no existe todavia (primera vez que se abre la app), usa
        los datos de ejemplo de main.py como semilla inicial -- nunca
        devuelve los mismos objetos que recibio, para que mutarlos despues
        no afecte a esos valores por defecto."""
        try:
            with open(DOCS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('pending', default_pending), data.get('recent', default_recent)
        except FileNotFoundError:
            return list(default_pending), list(default_recent)
        except (IOError, OSError, json.JSONDecodeError) as exc:
            print('DataManager: no se pudo leer documentos.json (%s) -- '
                  'se usan los datos de ejemplo' % exc)
            return list(default_pending), list(default_recent)

    def save_documents(self, pending, recent):
        """Guarda el estado actual de PENDING/RECENT. Se llama cada vez
        que se firma un documento (InterfazRRHHApp.complete_signature())."""
        try:
            with open(DOCS_FILE, 'w', encoding='utf-8') as f:
                json.dump({'pending': pending, 'recent': recent}, f,
                         indent=2, ensure_ascii=False)
            return True
        except (IOError, OSError) as exc:
            print('DataManager: no se pudo guardar documentos.json (%s)' % exc)
            return False

    # ============================================================ SOLICITUDES
    def load_requests(self):
        """Devuelve (solicitudes, notificaciones) guardadas en
        solicitudes.json: las peticiones de vacaciones/permiso/licencia y las
        notificaciones aun no leidas. ([], []) si no existe o esta corrupto."""
        try:
            with open(REQUESTS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return list(data.get('requests', [])), list(data.get('notifications', []))
        except FileNotFoundError:
            return [], []
        except (IOError, OSError, json.JSONDecodeError, AttributeError) as exc:
            print('DataManager: no se pudo leer solicitudes.json (%s)' % exc)
            return [], []

    def save_requests(self, requests, notifications):
        try:
            with open(REQUESTS_FILE, 'w', encoding='utf-8') as f:
                json.dump({'requests': requests, 'notifications': notifications},
                          f, indent=2, ensure_ascii=False)
            return True
        except (IOError, OSError) as exc:
            print('DataManager: no se pudo guardar solicitudes.json (%s)' % exc)
            return False

# -*- coding: utf-8 -*-
"""
main.py — Interfaz de Recursos Humanos (Kivy + KivyMD)
Arquitectura de la Sesion 12: "KV Language y la separacion de la logica".

Este archivo NO arma la interfaz visual: solo declara clases (como pide la
diapositiva "El motor logico en Python") con sus propiedades y sus metodos
de evento. El diseno completo (que widget va donde, colores, tamanos) vive
en interfazrrhh.kv, que Kivy carga solo porque la clase de la App se llama
InterfazRRHHApp -> busca "interfazrrhh.kv" (diapositiva "Magia pura").

La app hereda de MDApp (KivyMD), igual que:

    from kivymd.app import MDApp
    class FormularioApp(MDApp):
        def build(self):
            return FormularioAS()

Solo hay una excepcion deliberada: los datos de ejemplo (PENDING / RECENT)
se recorren aqui para poblar las tarjetas, porque son datos, no diseno —
igual que en la diapositiva "Interconexion: imprimir en la terminal los
datos leidos a traves de 'ids'".

Nada se guarda, se envia ni se genera como archivo: la app es solo la
maqueta visual, sin funcionalidades reales.

Ejecutar:  python main.py
"""
from kivy.config import Config
Config.set('graphics', 'width', '420')
Config.set('graphics', 'height', '880')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from datetime import datetime

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import (BooleanProperty, ListProperty, NumericProperty,
                             StringProperty)
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition

# ── KivyMD ──────────────────────────────────────────────────────────────────
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout

import theme as T
from widgets import GlassCard, MeshBackground, Pressable, PressCard, SnapshotBackground
import remote_config
import notifications
from data_manager import DataManager

# ---------------------------------------------------------------- OPCIONES
SHOW_DESKTOP_CTA = False   # Default Local -> True = agrega "¿No iniciaste sesión?"
ENTRY_ANIMATION = True     # animación de entrada al abrir la app

# -------------------------------------------------------- REMOTE CONFIG
# URL real en GitHub (raw) del JSON que arma remote_config.fetch(). Al
# iniciar, la app YA se ve completa con SHOW_DESKTOP_CTA/RECENT de arriba
# (Default Local); si esta URL responde, sus valores los reemplazan sin
# reiniciar la app (Activate). Si no hay internet o el archivo no existe
# todavia en GitHub, la app sigue igual, sin trabarse (Fallback) -- ver
# remote_config.py y InterfazRRHHApp._apply_remote_config().
REMOTE_CONFIG_URL = ('https://raw.githubusercontent.com/zikness/FirmApp/'
                      'main/remote/config.json')

# ------------------------------------------------------------------- DATOS
# (Igual que en la diapositiva del taller: esto es la "interconexion" de
#  datos, no diseno visual — por eso vive en .py y no en .kv)
# DEFAULT_* son la semilla de la PRIMERA vez que se abre la app (no hay
# datos previos guardados todavia). Una vez que exista data/documentos.json
# (ver data_manager.py), PENDING/RECENT se cargan de ahi -- asi un
# documento firmado sigue firmado aunque se cierre y se vuelva a abrir la
# app (Criterio B de la Sesion 24: "los datos criticos persisten entre
# ejecuciones").
DEFAULT_PENDING = [
    dict(doc_type='Contrato', title='Contrato de Trabajo Indefinido',
         deadline='17 Sep 2026', urgent=True, pages=4),
    dict(doc_type='Liquidación', title='Liquidación de Sueldo — Agosto 2026',
         deadline='20 Sep 2026', urgent=False, pages=2),
]

DEFAULT_RECENT = [
    dict(name='Liquidación Julio 2026',   date='01 Aug 2026', filesize='142 KB', offline=True),
    dict(name='Liquidación Junio 2026',   date='02 Jul 2026', filesize='138 KB', offline=True),
    dict(name='Liquidación Mayo 2026',    date='01 Jun 2026', filesize='145 KB', offline=False),
    dict(name='Contrato Renovación 2026', date='15 Jan 2026', filesize='512 KB', offline=True),
]

DM = DataManager()
PENDING, RECENT = DM.load_documents(DEFAULT_PENDING, DEFAULT_RECENT)


# ============================================================= COMPONENTES
# Cada clase de aqui tiene su regla <NombreClase>: en interfazrrhh.kv con
# TODO el diseno (hijos, colores, tamanos). En Python solo hay propiedades
# (para poder enlazarlas desde el .kv, ej. "text: root.title") y metodos
# de evento (a los que el .kv llama con on_release: root.mi_metodo()).

class StatCard(PressCard):
    """Una de las 3 tarjetas de estadisticas del encabezado."""
    value = StringProperty('')
    sub = StringProperty('')


class QuickActionCard(PressCard):
    """Una de las 3 tarjetas de 'Acciones Rápidas'."""
    icon_name = StringProperty('file')
    label_text = StringProperty('')
    sub_text = StringProperty('')
    c1 = ListProperty([1, 1, 1, 1])
    c2 = ListProperty([1, 1, 1, 1])


class SectionLabel(MDBoxLayout):
    """Encabezado de seccion ('TAREAS PENDIENTES', con o sin contador)."""
    title = StringProperty('')
    count = NumericProperty(-1)        # -1 = no mostrar contador


class HeaderCard(GlassCard):
    """Encabezado con saludo, nombre y avatar."""
    greeting = StringProperty('')

    def on_kv_post(self, base_widget):
        hour = datetime.now().hour
        self.greeting = ('Buenos días' if hour < 12 else
                         'Buenas tardes' if hour < 19 else 'Buenas noches')


class PendingCard(GlassCard):
    """Tarjeta de 'Tareas Pendientes' (Contrato / Liquidación por firmar)."""
    doc_type = StringProperty('')
    title = StringProperty('')
    deadline = StringProperty('')
    pages = NumericProperty(0)
    urgent = BooleanProperty(False)

    def sign_pressed(self):
        """El .kv llama esto con on_release: root.sign_pressed()."""
        MDApp.get_running_app().go_to_sign(self.doc_type, self.title,
                                           self.deadline, self.pages)


class DocRow(Pressable, MDBoxLayout):
    """Fila de 'Liquidaciones Recientes'."""
    name = StringProperty('')
    date = StringProperty('')
    filesize = StringProperty('')
    offline = BooleanProperty(False)
    last = BooleanProperty(False)

    def on_hover(self, hovering):
        Animation.cancel_all(self, 'md_bg_color')
        target = T.rgba(T.PRIMARY, 0.06) if hovering else (0, 0, 0, 0)
        Animation(md_bg_color=target, d=0.15).start(self)


class FooterCard(GlassCard):
    """Barra inferior fija 'Firma sin iniciar sesión'."""
    def sign_pressed(self):
        if not PENDING:
            return
        d = PENDING[0]
        MDApp.get_running_app().go_to_sign(d['doc_type'], d['title'],
                                           d['deadline'], d['pages'])


class DesktopCtaCard(GlassCard):
    """Tarjeta oscura '¿No iniciaste sesión?' (solo si SHOW_DESKTOP_CTA)."""
    def sign_pressed(self):
        if not PENDING:
            return
        d = PENDING[0]
        MDApp.get_running_app().go_to_sign(d['doc_type'], d['title'],
                                           d['deadline'], d['pages'])


# =============================================================== TARJETA DE FIRMA
class SignPanel(GlassCard):
    """
    Tarjeta 'Firmar con 1 toque' (encabezado, pestañas, boton CTA,
    disclaimer). Todo el "cascaron" esta en la regla <SignPanel>: de
    interfazrrhh.kv. Aqui solo vive la logica: cambiar de pestaña, validar
    el RUT, reaccionar al dibujo de la firma — el equivalente a
    "on_press: root.guardar_datos()" de la diapositiva de eventos.

    Vive dentro de SignScreen, una pantalla real del ScreenManager: al
    firmar ya NO se sustituye a si misma por una pantalla de exito (como
    hacia el modal original alternando 'chrome'/'body'); en su lugar le
    pide a la app que navegue a la pantalla 'success' (ver sign()).
    """
    doc_type = StringProperty('')
    title = StringProperty('')
    deadline = StringProperty('')
    pages = NumericProperty(0)
    tab = StringProperty('rut')
    HEIGHTS = {'rut': dp(388), 'draw': dp(476)}

    def on_kv_post(self, base_widget):
        self._rut_valid = False
        self._has_signature = False
        self.height = self.HEIGHTS['rut']
        self.set_tab('rut', animate=False)

    def reset_for(self, doc_type, title, deadline, pages):
        """Carga un documento nuevo y vuelve al estado inicial (pestaña RUT,
        boton deshabilitado). Lo llama SignScreen cada vez que se entra a
        la pantalla, para que un documento firmado antes no deje su RUT o
        su firma dibujada visibles en el siguiente."""
        self.doc_type = doc_type
        self.title = title
        self.deadline = deadline
        self.pages = pages
        self._rut_valid = False
        self._has_signature = False
        self.set_tab('rut', animate=False)

    # ------------------------------------------------------------- pestanas
    def set_tab(self, tab, animate=True):
        self.tab = tab
        for key, btn in (('rut', self.ids.tab_rut), ('draw', self.ids.tab_draw)):
            active = (key == tab)
            target = (1, 1, 1, 1) if active else (1, 1, 1, 0)
            Animation.cancel_all(btn, 'md_bg_color')
            if animate:
                Animation(md_bg_color=target, d=0.18).start(btn)
            else:
                btn.md_bg_color = target
            btn.fg_color = T.C_PRIMARY if active else T.C_SECONDARY

        # El contenido de la pestaña se reconstruye desde cero, asi que su
        # validez tambien: sin este reinicio, el boton "Firmar" quedaba
        # habilitado al volver a una pestaña cuyo campo ya se ve vacio.
        if tab == 'rut':
            self._rut_valid = False
        else:
            self._has_signature = False

        self.ids.content.clear_widgets()
        if tab == 'rut':
            view = Factory.RutTabContent()
            view.ids.rut_input.bind(on_rut_valid=lambda i, v: self._on_rut_valid(v))
            self._rut_view = view
        else:
            view = Factory.DrawTabContent()
            view.ids.pad.bind(on_signature_change=lambda i, v: self._on_draw_change(v))
            view.ids.clear_btn.bind(on_release=lambda *a: view.ids.pad.clear())
            self._draw_view = view
        self.ids.content.add_widget(view)

        if animate:
            self.ids.content.opacity = 0
            Animation(opacity=1, d=0.2, t='out_quad').start(self.ids.content)
        Animation.cancel_all(self, 'height')
        Animation(height=self.HEIGHTS[tab], d=0.22 if animate else 0,
                  t='out_quad').start(self)
        self._refresh_cta()

    # ----------------------------------------------------------- reacciones
    def _on_rut_valid(self, valid):
        self._rut_valid = bool(valid)
        view = self._rut_view
        borde = T.rgba(T.PRIMARY, 1) if valid else T.rgba(T.BG, 1)
        fondo = T.rgba(T.PRIMARY, .06) if valid else (1, 1, 1, .7)
        Animation.cancel_all(view.ids.field)
        Animation(line_color=borde, md_bg_color=fondo, d=0.18).start(view.ids.field)
        Animation.cancel_all(view.ids.check, 'opacity')
        Animation(opacity=1 if valid else 0, d=0.18).start(view.ids.check)
        self._refresh_cta()

    def _on_draw_change(self, has_signature):
        self._has_signature = has_signature
        view = self._draw_view
        Animation(opacity=0 if has_signature else 1, d=0.2).start(view.ids.hint)
        Animation(opacity=1 if has_signature else 0, d=0.2).start(view.ids.clear_btn)
        view.ids.clear_btn.disabled = not has_signature
        self._refresh_cta()

    def _refresh_cta(self):
        ok = getattr(self, '_rut_valid', False) if self.tab == 'rut' \
            else getattr(self, '_has_signature', False)
        self.ids.cta.set_enabled(ok)

    # --------------------------------------------------------------- firmar
    def sign(self):
        """No valida una firma digital real (no hay certificado ni
        backend) -- pero SI queda un registro real: el documento pasa de
        PENDING a RECENT y se guarda en JSON (ver
        InterfazRRHHApp.complete_signature(), data_manager.py)."""
        app = MDApp.get_running_app()
        app.complete_signature(self.doc_type, self.title, self.deadline, self.pages)
        app.go_to_success(self.title)

    # --------------------------------------------------------------- cerrar
    def close(self):
        MDApp.get_running_app().go_home()


# ============================================================ PANTALLAS (SCREENS)
# Las 4 pantallas navegables de la maqueta: Login, Inicio, Firmar y Exito.
# Cada una es una kivy.uix.screenmanager.Screen; el ScreenManager (creado en
# InterfazRRHHApp.build()) las muestra/oculta con una transicion animada al
# cambiar 'sm.current'. El diseno de cada pantalla vive en su regla
# <XScreen>: de interfazrrhh.kv -- aqui solo la logica de navegacion.

class LoginScreen(Screen):
    """
    Pantalla 'Iniciar sesion' -- la primera que ve el usuario. Valida el
    formato del identificador (RUT chileno con digito verificador real, o
    correo con formato nombre@dominio.com -- ver validators.py) y que la
    contrasena no este vacia, y habilita 'Ingresar' solo cuando ambos
    tienen formato valido.

    login() SI autentica de verdad contra las cuentas guardadas en
    usuarios.json (data_manager.py, Criterio B de la Sesion 24: "Login
    validado... persisten entre ejecuciones"). Si el formato es valido
    pero la cuenta no existe o la contrasena no coincide, se avisa en
    'auth_feedback' sin navegar a ningun lado.
    """
    def on_kv_post(self, base_widget):
        self._id_valid = False
        self._password_ok = False
        self._refresh_cta()

    def set_id_valid(self, valid):
        self._id_valid = bool(valid)
        self.ids.auth_feedback.text = ''
        self._refresh_cta()

    def set_password_filled(self, text):
        self._password_ok = len(text) >= 4
        self.ids.auth_feedback.text = ''
        self._refresh_cta()

    def _refresh_cta(self):
        ok = getattr(self, '_id_valid', False) and getattr(self, '_password_ok', False)
        self.ids.cta.set_enabled(ok)

    def login(self):
        app = MDApp.get_running_app()
        identifier = self.ids.identifier.text
        password = self.ids.password.text
        if app.dm.authenticate(identifier, password):
            self.ids.auth_feedback.text = ''
            app.go_to_home_after_login()
        else:
            self.ids.auth_feedback.text = (
                'RUT/correo o contraseña incorrectos. '
                '¿Todavía no tienes cuenta? Regístrate abajo.')


class RegisterScreen(Screen):
    """
    Pantalla 'Crear cuenta'. Valida formato (igual que LoginScreen) mas
    que la confirmacion de contrasena coincida, y registra la cuenta de
    verdad en usuarios.json (data_manager.py). Si se crea con exito, entra
    directo a Inicio -- registro + login combinados en un solo paso, como
    en el "Happy Path" de la demo (Registro e Ingreso -> Creacion de Datos
    -> ...).
    """
    def on_kv_post(self, base_widget):
        self._id_valid = False
        self._password_ok = False
        self._confirm_ok = False
        self._refresh_cta()

    def set_id_valid(self, valid):
        self._id_valid = bool(valid)
        self.ids.feedback.text = ''
        self._refresh_cta()

    def set_password_filled(self, text):
        self._password_ok = len(text) >= 4
        self._check_confirm()
        self.ids.feedback.text = ''
        self._refresh_cta()

    def set_confirm_filled(self, text):
        self._check_confirm()
        self.ids.feedback.text = ''
        self._refresh_cta()

    def _check_confirm(self):
        self._confirm_ok = (self.ids.password.text != '' and
                            self.ids.password.text == self.ids.confirm.text)

    def _refresh_cta(self):
        ok = (getattr(self, '_id_valid', False) and
              getattr(self, '_password_ok', False) and
              getattr(self, '_confirm_ok', False))
        self.ids.cta.set_enabled(ok)

    def register(self):
        app = MDApp.get_running_app()
        identifier = self.ids.identifier.text
        password = self.ids.password.text
        ok, mensaje = app.dm.register_user(identifier, password)
        self.ids.feedback.text = mensaje
        self.ids.feedback.text_color = (T.C_PRIMARY if ok else
                                        T.rgba(T.ORANGE, .95))
        if ok:
            app.go_to_home_after_login()

    def reset(self):
        """Limpia el formulario al entrar (para no dejar datos de una
        cuenta anterior si el usuario vuelve a abrir esta pantalla)."""
        self.ids.identifier.text = ''
        self.ids.password.text = ''
        self.ids.confirm.text = ''
        self.ids.feedback.text = ''
        self._id_valid = self._password_ok = self._confirm_ok = False
        self._refresh_cta()


class HomeScreen(Screen):
    """Pantalla 'Inicio': envuelve el tablero (RootScreen) sin logica propia."""
    pass


class SignScreen(Screen):
    """Pantalla 'Firmar': aloja el SignPanel con los datos del documento
    elegido en Inicio."""
    def load_document(self, doc_type, title, deadline, pages):
        self.ids.panel.reset_for(doc_type, title, deadline, pages)


class SuccessScreen(Screen):
    """Pantalla 'Exito': confirma la firma y vuelve a Inicio."""
    doc_title = StringProperty('')

    def close(self):
        MDApp.get_running_app().go_home()


# ------------------------------------------------------------------- ROOT
class RootScreen(MeshBackground):
    """Contenido del tablero (Inicio). Puebla las listas dinamicas (datos,
    no diseno). No es la Screen en si -- HomeScreen la envuelve en el .kv --
    para poder reutilizar tal cual toda la logica de animacion de entrada.

    banner_text y los metodos set_desktop_cta_visible()/set_max_recent()
    son el punto donde Remote Config conecta con la pantalla: arrancan con
    el valor local (Default) y InterfazRRHHApp los vuelve a llamar si llega
    una configuracion remota valida (ver _apply_remote_config() mas abajo).
    """
    banner_text = StringProperty('')   # vacio = el banner no se muestra
    pending_count = NumericProperty(0)  # cuantos PENDING hay (badge + stat)
    max_recent = NumericProperty(0)    # ultimo limite aplicado (local o remoto)

    def on_kv_post(self, base_widget):
        self.refresh_pending()
        self.set_max_recent(len(RECENT))
        self.set_desktop_cta_visible(SHOW_DESKTOP_CTA)
        if ENTRY_ANIMATION:
            Clock.schedule_once(self._entry_animation, 0)

    def refresh_pending(self):
        """Repuebla 'Tareas Pendientes' desde PENDING (datos.py / JSON) y
        mantiene el contador (badge de la seccion + tarjeta 'sin firma')
        en sincronia -- se llama al abrir la app y despues de firmar un
        documento (ver InterfazRRHHApp.complete_signature())."""
        self.ids.pending_box.clear_widgets()
        for doc in PENDING:
            self.ids.pending_box.add_widget(PendingCard(**doc))
        self.pending_count = len(PENDING)

    def set_desktop_cta_visible(self, visible):
        """Feature flag remoto: muestra/oculta 'Firmar sin sesión' sin
        reiniciar la app."""
        self.ids.extra_box.clear_widgets()
        if visible:
            self.ids.extra_box.add_widget(DesktopCtaCard())

    def set_max_recent(self, n):
        """Limite numerico remoto: cuantas 'Liquidaciones Recientes' se
        listan (siempre sobre los mismos datos de RECENT). Se guarda en
        'max_recent' para poder repetir el mismo limite despues de firmar
        un documento nuevo, sin perder lo que trajo Remote Config."""
        self.max_recent = n
        docs = RECENT[:max(0, n)]
        self.ids.docs_box.clear_widgets()
        total = len(docs)
        for i, doc in enumerate(docs):
            self.ids.docs_box.add_widget(DocRow(last=(i == total - 1), **doc))

    def _entry_animation(self, dt):
        widgets = list(self.ids.col.children)[::-1]
        for i, w in enumerate(widgets):
            w.opacity = 0
            Clock.schedule_once(
                lambda dt, w=w: Animation(opacity=1, d=0.35,
                                          t='out_quad').start(w),
                i * 0.05)
        self.ids.footer.opacity = 0
        Clock.schedule_once(
            lambda dt: Animation(opacity=1, d=0.35).start(self.ids.footer),
            0.45)


# =================================================== AVISO DE NOTIFICACIONES
class NotificationOverlay(MDFloatLayout):
    """
    Superposicion liviana que muestra, en grande, la notificacion actual
    (el banner de Remote Config y/o el aviso de documentos urgentes). La
    abre el boton de la campana de HeaderCard o el banner del Dashboard
    (on_release: app.show_notifications()).

    No es una Screen del ScreenManager -- es informativa y transitoria,
    no forma parte del flujo de navegacion -- asi que se agrega/quita de
    HomeScreen igual que el ModalOverlay de la v1, pero sin repetir su
    fuga de memoria: Pressable (widgets.py) ya desconecta su listener de
    Window al salir del arbol de widgets (ver on_parent en widgets.py).
    """
    message = StringProperty('')
    urgent_count = NumericProperty(0)

    def close(self):
        MDApp.get_running_app().hide_notifications()

    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            return True
        if self.get_root_window() and not self.ids.card.collide_point(*touch.pos):
            self.close()
            return True
        return True


# ------------------------------------------------------------------- APP
class InterfazRRHHApp(MDApp):
    """
    App de KivyMD. El nombre de esta clase (InterfazRRHHApp -> 'interfazrrhh')
    es lo que hace que Kivy cargue interfazrrhh.kv automaticamente, sin ningun
    Builder.load_file() manual (diapositiva 'Magia pura').
    """
    title = 'Interfaz de Recursos Humanos'

    def build(self):
        # Tema Material ajustado a la paleta del diseno de Figma.
        # Como cada widget fija sus colores explicitamente en el .kv, el tema
        # no altera el diseno: solo define los valores por defecto de KivyMD.
        self.theme_cls.theme_style = 'Light'
        self.theme_cls.primary_palette = 'BlueGray'   # el mas cercano a #5C7E8F
        self.theme_cls.accent_palette = 'Gray'
        self.theme_cls.material_style = 'M3'

        Window.size = (420, 880)
        Window.clearcolor = T.rgba(T.BG)

        # Persistencia (data_manager.py): una sola instancia de
        # DataManager para toda la app -- la misma que ya cargo
        # PENDING/RECENT al importar este modulo. 'self.dm' es el punto
        # donde el resto del codigo (LoginScreen, RegisterScreen, firmar
        # un documento) la encuentra.
        self.dm = DM

        # ScreenManager con las 5 pantallas navegables de la maqueta:
        # Login -> Registro -> Inicio (tablero) -> Firmar (RUT / dibujar
        # firma) -> Exito. Cada pantalla se crea una sola vez y persiste
        # durante toda la sesion; navegar solo cambia cual esta visible
        # (sm.current), no crea ni destruye widgets como hacia el modal
        # original. LoginScreen se agrega primero -> es la que el
        # ScreenManager muestra al abrir.
        self.sm = ScreenManager(transition=FadeTransition(duration=0.16))
        self.login_screen = LoginScreen(name='login')
        self.register_screen = RegisterScreen(name='register')
        self.home_screen = HomeScreen(name='home')
        self.sign_screen = SignScreen(name='sign')
        self.success_screen = SuccessScreen(name='success')
        for screen in (self.login_screen, self.register_screen,
                       self.home_screen, self.sign_screen, self.success_screen):
            self.sm.add_widget(screen)
        self.notification_overlay = None

        # Remote Config: la app ya arranco completa con los valores locales
        # (SHOW_DESKTOP_CTA, RECENT) -- este fetch es "best effort" en
        # segundo plano y puede llegar antes o despues de que el usuario ya
        # este mirando la pantalla. Si falla, no pasa nada (ver
        # remote_config.py y _apply_remote_config() mas abajo).
        remote_config.fetch(REMOTE_CONFIG_URL, on_loaded=self._apply_remote_config)

        return self.sm

    def _apply_remote_config(self, cfg):
        """Se llama SOLO si remote_config.fetch() trajo un JSON valido
        (Activate). Si nunca se llama -- sin internet, servidor caido, JSON
        todavia no existe en GitHub -- la app sigue con lo que ya tenia
        (Fallback), sin que haga falta ningun 'else' aqui."""
        dashboard = self.home_screen.ids.dashboard
        dashboard.banner_text = cfg['banner_message']
        dashboard.set_desktop_cta_visible(cfg['show_desktop_cta'])
        dashboard.set_max_recent(cfg['max_recent_docs'])

    # ---------------------------------------------------- notificaciones
    def show_notifications(self):
        """Abre el aviso grande de notificaciones (boton de campana del
        Dashboard, o el banner de Remote Config). Si ya esta abierto, no
        hace nada -- igual que open_modal() en la version anterior."""
        if self.notification_overlay:
            return
        dashboard = self.home_screen.ids.dashboard
        overlay = Factory.NotificationOverlay()
        overlay.message = dashboard.banner_text
        overlay.urgent_count = sum(1 for d in PENDING if d.get('urgent'))
        self.notification_overlay = overlay
        self.home_screen.add_widget(overlay)
        overlay.opacity = 0
        Animation(opacity=1, d=0.16, t='out_quad').start(overlay)

    def hide_notifications(self):
        if not self.notification_overlay:
            return
        overlay, self.notification_overlay = self.notification_overlay, None
        anim = Animation(opacity=0, d=0.16, t='in_quad')
        anim.bind(on_complete=lambda *a: self.home_screen.remove_widget(overlay))
        anim.start(overlay)

    # --------------------------------------------------------- navegacion
    def go_to_register(self):
        """Login -> Registro."""
        self.register_screen.reset()
        self.sm.current = 'register'

    def go_to_login(self):
        """Registro -> Login (volver sin crear cuenta)."""
        self.sm.current = 'login'

    def go_to_home_after_login(self):
        """Login o Registro -> Inicio. Llamado por LoginScreen.login() y
        por RegisterScreen.register() cuando la cuenta se crea con exito
        (registro + login combinados, ver RegisterScreen)."""
        self.sm.current = 'home'
        # Notificaciones (Plyer): si al entrar ya hay un documento urgente,
        # se avisa una vez al sistema operativo -- el mismo lugar donde
        # iria una notificacion push real si el proyecto tuviera backend.
        # Va aqui (despues de "iniciar sesion") y no en build(), porque no
        # tendria sentido notificar antes de que el usuario se identifique.
        if any(doc.get('urgent') for doc in PENDING):
            notifications.notify(
                'Tienes documentos urgentes',
                'Hay %d documento(s) pendiente(s) por firmar.' %
                sum(1 for d in PENDING if d.get('urgent')))

    def go_to_sign(self, doc_type, title, deadline, pages):
        """Inicio -> Firmar. Llamado desde 'Firmar con 1 toque' / 'Firmar'."""
        self._snapshot_home()
        self.sign_screen.load_document(doc_type, title, deadline, pages)
        self.sm.current = 'sign'

    def go_to_success(self, doc_title):
        """Firmar -> Exito. Llamado por SignPanel.sign()."""
        self.success_screen.doc_title = doc_title
        # Reusa la misma foto del Dashboard que ya tiene SignScreen, para
        # que el fondo oscurecido no "salte" entre una pantalla y la otra.
        self.success_screen.ids.bg_image.set_texture(self.sign_screen.ids.bg_image.get_texture())
        self.sm.current = 'success'
        notifications.notify('Documento firmado',
                             '%s se firmó correctamente.' % doc_title)

    def go_home(self):
        """Firmar o Exito -> Inicio. Cierra el flujo de firma."""
        self.sm.current = 'home'

    def complete_signature(self, doc_type, title, deadline, pages):
        """Pasa un documento de PENDING a RECENT y lo persiste en JSON
        (data_manager.py) -- Criterio B de la Sesion 24: el documento
        firmado sigue firmado aunque se cierre y se vuelva a abrir la app.
        Llamado por SignPanel.sign() antes de navegar a Exito."""
        PENDING[:] = [d for d in PENDING if d['title'] != title]
        RECENT.insert(0, dict(
            name=title,
            date=datetime.now().strftime('%d %b %Y'),
            filesize='—',
            offline=True,
        ))
        self.dm.save_documents(PENDING, RECENT)
        dashboard = self.home_screen.ids.dashboard
        dashboard.refresh_pending()
        dashboard.set_max_recent(dashboard.max_recent)

    def _snapshot_home(self):
        """Foto del Dashboard tal como se ve justo antes de ir a Firmar, para
        pintarla (oscurecida) detras de la tarjeta -- el efecto 'modal
        flotante sobre fondo oscurecido' de la v1, pero sin volver a crear
        y destruir un overlay cada vez (lo que causaba la fuga de memoria
        de antes): HomeScreen nunca se destruye, solo se fotografia."""
        imagen = self.home_screen.export_as_image()
        textura = imagen.texture
        # El Fbo que usa export_as_image() entrega la textura con el eje Y
        # invertido (un detalle conocido de Kivy); se corrige una sola vez
        # aqui, en el punto de captura -- go_to_success() reutiliza esta
        # misma textura ya corregida, sin volver a tocarla.
        textura.flip_vertical()
        self.sign_screen.ids.bg_image.set_texture(textura)


# Factory se usa para (a) instanciar desde Python las clases dinamicas
# declaradas con "@Base" en el .kv (RutTabContent, DrawTabContent), y
# (b) para que el .kv pueda encontrar por nombre las clases definidas en
# widgets.py y en este archivo. Kivy no las detecta solo con el "import";
# hay que registrarlas explicitamente.
from kivy.factory import Factory  # noqa: E402  (al final para evitar ciclos)
import widgets as _w  # noqa: E402

for _cls in (_w.GlassCard, _w.DashedPanel, _w.PressCard, _w.GradientTile,
             _w.Icon, _w.Dot, _w.Divider, _w.SolidButton, _w.IconTile,
             _w.IconButton, _w.Pill, _w.RutInput, _w.SignaturePad,
             _w.MeshBackground, _w.SnapshotBackground, _w.PressableBox,
             _w.LoginIdentifierInput, _w.PasswordInput,
             StatCard, QuickActionCard, SectionLabel, HeaderCard,
             PendingCard, DocRow, FooterCard, DesktopCtaCard,
             SignPanel, LoginScreen, RegisterScreen, HomeScreen, SignScreen, SuccessScreen,
             RootScreen, NotificationOverlay):
    Factory.register(_cls.__name__, cls=_cls)


if __name__ == '__main__':
    InterfazRRHHApp().run()

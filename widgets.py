# -*- coding: utf-8 -*-
"""
widgets.py
Clases base reutilizables, construidas sobre COMPONENTES DE KIVYMD
(MDBoxLayout, MDFloatLayout, MDCard, MDLabel, MDTextField...), tal como
pide la Sesion 12 ("Integrando componentes de KivyMD solicitados en el RA2").

Regla de la sesion: estas clases NO arman su arbol de hijos aqui.
Solo definen:
  (a) propiedades de Kivy para poder enlazarlas desde el .kv, y
  (b) el dibujo en canvas que Material Design no ofrece (el efecto de
      vidrio del diseno, los degradados y los iconos vectoriales).

El relleno, el radio y el borde de cada superficie los dibuja KivyMD con
sus propiedades nativas `md_bg_color`, `radius`, `line_color` y
`line_width` (heredadas de BackgroundColorBehavior). Toda la composicion
visual vive en interfazrrhh.kv — igual que <FormularioAS@MDBoxLayout>
del ejemplo de la diapositiva.
"""
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.graphics import (Color, RoundedRectangle, Rectangle, Line, Ellipse,
                           InstructionGroup, PushMatrix, PopMatrix, Scale)
from kivy.graphics.texture import Texture
from kivy.metrics import dp
from kivy.properties import (ListProperty, NumericProperty, StringProperty,
                             BooleanProperty)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.stencilview import StencilView

# ── Componentes de KivyMD (Material Design) ─────────────────────────────────
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.widget import MDWidget

import theme as T
from icons import ICONS, STROKE


# ============================================================== TEXTURAS
def linear_gradient(c1, c2, size=(64, 64)):
    """Degradado diagonal (arriba-izq -> abajo-der), como 'bg-gradient-to-br'."""
    w, h = size
    buf = bytearray()
    for y in range(h):
        v = 1.0 - (y / (h - 1))
        for x in range(w):
            u = x / (w - 1)
            t = (u + (1.0 - v)) / 2.0
            for i in range(3):
                buf.append(int(255 * (c1[i] * (1 - t) + c2[i] * t)))
            buf.append(255)
    tex = Texture.create(size=size, colorfmt='rgba')
    tex.blit_buffer(bytes(buf), colorfmt='rgba', bufferfmt='ubyte')
    return tex


def mesh_texture(size=(128, 220)):
    """Fondo .mesh-bg: base #D4DDE2 + dos manchas radiales azuladas."""
    w, h = size
    base = T.rgba(T.BG)
    blob = T.rgba(T.PRIMARY)
    spots = [(0.20, 0.10, 0.22, 0.80), (0.80, 0.80, 0.15, 0.80)]
    buf = bytearray()
    for py in range(h):
        ny = 1.0 - (py / (h - 1))
        for px in range(w):
            nx = px / (w - 1)
            r, g, b = base[0], base[1], base[2]
            for cx, cy, a, rad in spots:
                d = ((nx - cx) ** 2 + (ny - cy) ** 2) ** 0.5 / rad
                if d < 1.0:
                    k = a * (1.0 - d) ** 1.6
                    r = r * (1 - k) + blob[0] * k
                    g = g * (1 - k) + blob[1] * k
                    b = b * (1 - k) + blob[2] * k
            buf += bytes((int(r * 255), int(g * 255), int(b * 255), 255))
    tex = Texture.create(size=size, colorfmt='rgba')
    tex.blit_buffer(bytes(buf), colorfmt='rgba', bufferfmt='ubyte')
    return tex


class MeshBackground(MDFloatLayout):
    """
    Fondo degradado del diseno (MDFloatLayout de KivyMD + textura propia).
    RootScreen hereda de esta clase.
    """
    def __init__(self, **kw):
        super().__init__(**kw)
        self._tex = mesh_texture()
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self._rect = Rectangle(texture=self._tex, pos=self.pos, size=self.size)
        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *a):
        self._rect.pos = self.pos
        self._rect.size = self.size


class SnapshotBackground(MDFloatLayout):
    """
    Pinta una textura arbitraria de fondo (ej. una foto del Dashboard
    tomada con Widget.export_as_image(), ver InterfazRRHHApp._snapshot_home
    en main.py) con un velo oscuro semitransparente encima -- el efecto
    "modal flotante sobre fondo oscurecido" de SignScreen/SuccessScreen.

    No se usa el widget Image de Kivy para esto: Image espera cargar su
    textura a traves de su propiedad `source` (un archivo), y asignarle
    `.texture` a mano no actualiza su calculo interno de tamano de render
    (`norm_image_size`), asi que la imagen terminaba dibujandose diminuta y
    mal ubicada. Dibujar con kivy.graphics directamente (igual que
    MeshBackground arriba) evita por completo ese problema.
    """
    def __init__(self, **kw):
        super().__init__(**kw)
        with self.canvas:
            self._color = Color(1, 1, 1, 1)
            self._rect = Rectangle(pos=self.pos, size=self.size)
            Color(*T.rgba(T.TEXT, 0.45))
            self._veil = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._sync, size=self._sync)

    def set_texture(self, texture):
        """Reemplaza la foto de fondo. texture=None deja el area transparente
        (antes de la primera foto, o si export_as_image llegara a fallar)."""
        self._rect.texture = texture
        self._color.a = 1 if texture is not None else 0

    def get_texture(self):
        """La textura actual, para pasarsela tal cual a otro
        SnapshotBackground (ver InterfazRRHHApp.go_to_success en main.py,
        que reusa la foto de SignScreen en vez de tomar una nueva)."""
        return self._rect.texture

    def _sync(self, *a):
        self._rect.pos = self._veil.pos = self.pos
        self._rect.size = self._veil.size = self.size


# ============================================================== TARJETAS
class GlassCard(MDBoxLayout):
    """
    Equivalente a .glass-card / .glass-card-dark / .glass-modal del CSS.

    El relleno, el radio y el borde los pinta KivyMD con `md_bg_color`,
    `radius` y `line_color` (propiedades nativas de MDBoxLayout). Lo unico
    que agrega esta clase es la SOMBRA difusa por capas del diseno, que
    Material Design no reproduce: se inserta al inicio de canvas.before
    para quedar por DEBAJO del fondo que dibuja KivyMD.
    """
    shadow = BooleanProperty(True)
    shadow_strength = NumericProperty(1.0)

    SPREADS = ((dp(12), 0.030), (dp(7), 0.038), (dp(3), 0.045))

    def __init__(self, **kw):
        super().__init__(**kw)
        self._sh_color, self._sh_rect = [], []
        grupo = InstructionGroup()
        for spread, alpha in self.SPREADS:
            col = Color(*T.rgba(T.PRIMARY, alpha))
            rect = RoundedRectangle()
            grupo.add(col)
            grupo.add(rect)
            self._sh_color.append(col)
            self._sh_rect.append(rect)
        # index 0 => detras del fondo que dibuja KivyMD
        self.canvas.before.insert(0, grupo)
        self.bind(pos=self._update_shadow, size=self._update_shadow,
                  radius=self._update_shadow,
                  shadow_strength=self._update_shadow_colors,
                  shadow=self._update_shadow_colors)
        self._update_shadow()
        self._update_shadow_colors()

    def _radio(self):
        """`radius` de KivyMD es una lista de 4 valores; tomamos el primero."""
        r = self.radius
        return r[0] if isinstance(r, (list, tuple)) else r

    def _update_shadow(self, *a):
        rad = self._radio()
        for (spread, _), rect in zip(self.SPREADS, self._sh_rect):
            rect.pos = (self.x - spread, self.y - spread - dp(2))
            rect.size = (self.width + spread * 2, self.height + spread * 2)
            rect.radius = [rad + spread] * 4

    def _update_shadow_colors(self, *a):
        k = self.shadow_strength if self.shadow else 0
        for (_, alpha), col in zip(self.SPREADS, self._sh_color):
            col.rgba = T.rgba(T.PRIMARY, alpha * k)


class DashedPanel(MDBoxLayout):
    """
    MDBoxLayout con borde punteado (el marco del lienzo de firma).
    KivyMD dibuja el relleno con `md_bg_color`; el punteado se agrega aqui
    porque `line_color` de Material Design solo traza lineas continuas.
    """
    dash_color = ListProperty((0, 0, 0, 0))
    dash_width = NumericProperty(1.6)

    def __init__(self, **kw):
        super().__init__(**kw)
        with self.canvas.after:
            self._c = Color(*self.dash_color)
            self._line = Line(width=self.dash_width, dash_length=7, dash_offset=5)
        self.bind(pos=self._update, size=self._update, radius=self._update,
                  dash_color=self._update_color, dash_width=self._update_color)
        self._update()
        self._update_color()

    def _update(self, *a):
        r = self.radius
        rad = r[0] if isinstance(r, (list, tuple)) else r
        self._line.rounded_rectangle = (self.x, self.y, self.width,
                                        self.height, rad)

    def _update_color(self, *a):
        self._c.rgba = self.dash_color
        self._line.width = self.dash_width


class GradientTile(MDFloatLayout):
    """Cuadro redondeado con degradado. c1/c2 son propiedades -> editables desde .kv."""
    tile_radius = NumericProperty(dp(16))
    c1 = ListProperty([1, 1, 1, 1])
    c2 = ListProperty([1, 1, 1, 1])

    def __init__(self, **kw):
        super().__init__(**kw)
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self._rect = RoundedRectangle(radius=[self.tile_radius] * 4)
        self._retexture()
        self.bind(pos=self._sync, size=self._sync, tile_radius=self._sync,
                  c1=self._retexture, c2=self._retexture)

    def _retexture(self, *a):
        self._rect.texture = linear_gradient(self.c1, self.c2)
        self._sync()

    def _sync(self, *a):
        self._rect.pos = self.pos
        self._rect.size = self.size
        self._rect.radius = [self.tile_radius] * 4


# ================================================ PULSADO Y HOVER (ANIMACION)
class Pressable(ButtonBehavior):
    """
    Reproduce el 'active:scale-[0.96]' y el 'hover:scale-[1.02]' del CSS
    original insertando una matriz de escala en el canvas del widget.
    """
    press_scale = NumericProperty(1.0)
    hover_enabled = BooleanProperty(True)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.canvas.before.insert(0, Scale(1, 1, 1))
        self.canvas.before.insert(0, PushMatrix())
        self._scale = self.canvas.before.children[1]
        self.canvas.after.add(PopMatrix())
        self._hovering = False
        self.bind(pos=self._sync_scale, size=self._sync_scale,
                  press_scale=self._sync_scale)
        Window.bind(mouse_pos=self._on_mouse)

    def on_parent(self, instance, parent):
        """Desconecta el listener de Window si el widget sale del arbol.

        Window.bind(mouse_pos=...) mantiene una referencia fuerte a este
        widget para siempre; sin este unbind, cada tarjeta creada y luego
        descartada (ej. al recrear contenido dinamico) quedaria colgada en
        memoria y seguiria recibiendo eventos de mouse.
        """
        if parent is None:
            Window.unbind(mouse_pos=self._on_mouse)

    def _sync_scale(self, *a):
        self._scale.origin = (self.center_x, self.center_y, 0)
        self._scale.x = self._scale.y = self.press_scale

    def _animate(self, value, duration=0.09, transition='out_quad'):
        Animation.cancel_all(self, 'press_scale')
        Animation(press_scale=value, d=duration, t=transition).start(self)

    def on_press(self):
        self._animate(0.96, 0.07)

    def on_release(self):
        self._animate(1.02 if self._hovering else 1.0, 0.13, 'out_back')

    def _on_mouse(self, window, pos):
        if not self.hover_enabled or not self.get_root_window() or self.disabled:
            return
        inside = self.collide_point(*self.to_widget(*pos))
        if inside != self._hovering:
            self._hovering = inside
            self._animate(1.02 if inside else 1.0, 0.14)
            self.on_hover(inside)

    def on_hover(self, hovering):
        """Se puede sobrescribir para cambiar colores al pasar el mouse."""
        pass


class PressCard(Pressable, GlassCard):
    """Tarjeta 'glass' que reacciona al toque y al mouse (Acciones Rapidas, stats)."""
    def on_hover(self, hovering):
        Animation.cancel_all(self, 'shadow_strength')
        Animation(shadow_strength=2.0 if hovering else 1.0, d=0.15).start(self)


# ================================================================ ICONOS
class Icon(MDWidget):
    """
    Dibuja un icono de icons.py escalando el lienzo 24x24.
    (No se usa MDIcon porque esa clase pinta iconos de una fuente tipografica
     y el diseno de Figma trae iconos vectoriales propios.)
    """
    name = StringProperty('file')
    color = ListProperty(T.C_PRIMARY)
    stroke = NumericProperty(0)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.bind(pos=self._redraw, size=self._redraw, name=self._redraw,
                  color=self._redraw)
        self._redraw()

    def _redraw(self, *a):
        self.canvas.clear()
        ops = ICONS.get(self.name)
        if not ops or self.width <= 0 or self.height <= 0:
            return
        s = min(self.width, self.height) / 24.0
        ox = self.x + (self.width - 24 * s) / 2.0
        oy = self.y + (self.height - 24 * s) / 2.0
        lw = (self.stroke or STROKE.get(self.name, 1.8)) * s * 0.62

        def P(x, y):
            return ox + x * s, oy + (24 - y) * s

        with self.canvas:
            Color(*self.color)
            for op in ops:
                kind = op[0]
                if kind == 'pl':
                    pts = []
                    for (x, y) in op[1]:
                        pts.extend(P(x, y))
                    Line(points=pts, width=lw, cap='round', joint='round')
                elif kind == 'c':
                    cx, cy = P(op[1], op[2])
                    Line(circle=(cx, cy, op[3] * s), width=lw)
                elif kind == 'r':
                    x, y, w, h, rad = op[1], op[2], op[3], op[4], op[5]
                    px, py = P(x, y + h)
                    Line(rounded_rectangle=(px, py, w * s, h * s, rad * s),
                         width=lw)


class Dot(MDWidget):
    """Circulo solido (punto de notificacion, badge de exito)."""
    color = ListProperty(T.C_PRIMARY)
    ring = BooleanProperty(False)

    def __init__(self, **kw):
        super().__init__(**kw)
        self._ring_e = None
        with self.canvas.before:
            if self.ring:
                Color(1, 1, 1, 1)
                self._ring_e = Ellipse(pos=self.pos, size=self.size)
            self._c = Color(*self.color)
            self._e = Ellipse(pos=self.pos, size=self.size)
        self.bind(pos=self._s, size=self._s, color=self._update_color)
        self._s()

    def _update_color(self, *a):
        self._c.rgba = self.color

    def _s(self, *a):
        if self._ring_e is not None:
            self._ring_e.pos, self._ring_e.size = self.pos, self.size
            p = dp(2)
            self._e.pos = (self.x + p, self.y + p)
            self._e.size = (self.width - 2 * p, self.height - 2 * p)
        else:
            self._e.pos, self._e.size = self.pos, self.size


class Divider(MDWidget):
    """
    Linea separadora de 1px (border-b del diseno).
    Se dibuja a mano en vez de usar MDSeparator para conservar el color
    exacto (#D4DDE2 al 85%) del prototipo de Figma.
    """
    color = ListProperty(T.C_DIVIDER)

    def __init__(self, **kw):
        super().__init__(**kw)
        with self.canvas:
            self._col = Color(*self.color)
            self._r = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._s, size=self._s,
                  color=lambda *a: setattr(self._col, 'rgba', self.color))

    def _s(self, *a):
        self._r.pos = self.pos
        self._r.size = (self.width, dp(1))


class SolidButton(Pressable, MDCard):
    """
    Boton del diseno, construido sobre MDCard (componente de KivyMD).
    MDCard aporta la superficie Material: `md_bg_color`, `radius`,
    `elevation` y `line_color`. Encima se le agrega el comportamiento de
    pulsado/hover y, desde el .kv, el icono vectorial + el MDLabel.

    (No se usa MDRaisedButton porque impone su propia sombra, su ripple y
     su tipografia en mayusculas, lo que alteraria el diseno de Figma.)
    """
    text = StringProperty('')
    icon_name = StringProperty('')
    fg_color = ListProperty((1, 1, 1, 1))

    def set_enabled(self, enabled):
        """Habilita/deshabilita visualmente el boton (usado por el modal de firma)."""
        self._recordar_colores()
        self.disabled = not enabled
        target_bg = self._on_bg if enabled else tuple(T.rgba(T.BG))
        target_fg = self._on_fg if enabled else tuple(T.C_SECONDARY)
        Animation.cancel_all(self, 'md_bg_color')
        Animation(md_bg_color=target_bg, d=0.2, t='out_quad').start(self)
        self.fg_color = target_fg

    def _recordar_colores(self):
        if not hasattr(self, '_on_bg'):
            self._on_bg = tuple(self.md_bg_color)
            self._on_fg = tuple(self.fg_color)

    def on_hover(self, hovering):
        if self.disabled:
            return
        self._recordar_colores()
        if self._on_bg == tuple(T.C_PRIMARY):
            target = tuple(T.C_PRIMARY_DARK) if hovering else self._on_bg
            Animation.cancel_all(self, 'md_bg_color')
            Animation(md_bg_color=target, d=0.15).start(self)


class IconTile(MDFloatLayout):
    """
    Cuadrado Material con un icono centrado (badge de documento).
    El fondo y el radio los pinta KivyMD (`md_bg_color`, `radius`).
    """
    icon_name = StringProperty('file')
    icon_color = ListProperty(T.C_PRIMARY)


class IconButton(Pressable, MDFloatLayout):
    """Boton cuadrado con icono vectorial (campana, cerrar modal)."""
    icon_name = StringProperty('file')
    icon_color = ListProperty(T.C_PRIMARY)

    def on_hover(self, hovering):
        if not hasattr(self, '_base_bg'):
            self._base_bg = tuple(self.md_bg_color)
        if self._base_bg[3] == 0:          # boton transparente: no hay hover
            return
        Animation.cancel_all(self, 'md_bg_color')
        target = T.C_TINT_20 if hovering else self._base_bg
        Animation(md_bg_color=target, d=0.15).start(self)


class Pill(MDBoxLayout):
    """
    Badge redondeado (MDBoxLayout de KivyMD) que se ajusta solo al ancho de
    su texto. El ajuste se hace en interfazrrhh.kv leyendo el texture_size
    del MDLabel interno — sin Python.
    """
    text = StringProperty('')
    fg_color = ListProperty(T.C_PRIMARY)
    icon_name = StringProperty('')


# ============================================================ CAMPO DE RUT
class RutInput(MDTextField):
    """
    Campo de RUT sobre MDTextField (componente de KivyMD), con formato
    automatico 12.345.678-9 — igual que formatRut() del prototipo de Figma.
    Solo valida el largo, para efecto visual.

    En el .kv se le apagan la linea y el relleno de Material
    (`line_color_normal`, `fill_color_normal`) para que el campo se vea
    como el del diseno: un recuadro redondeado propio.

    Dispara el evento on_rut_valid(bool), que el .kv puede enlazar.
    """
    def __init__(self, **kw):
        super().__init__(**kw)
        self._busy = False
        self.valid = None
        self.register_event_type('on_rut_valid')

    def on_rut_valid(self, valid):
        pass

    def set_default_colors(self, interval, updated=False):
        """
        Reemplaza a set_default_colors() de MDTextField.

        KivyMD considera que un color con valor [0, 0, 0, 0] esta "sin
        definir" y lo sustituye por uno del tema Material. Este campo
        necesita justamente lo contrario: que el subrayado, el borde y el
        relleno sean transparentes, porque el recuadro redondeado ya lo
        dibuja el MDBoxLayout que lo contiene. Por eso aqui los colores se
        copian tal cual, sin el relleno automatico del tema.
        """
        self._hint_text_color = self.hint_text_color_normal
        self._text_color_normal = self.text_color_normal
        self._fill_color = self.fill_color_normal
        self._line_color_normal = self.line_color_normal
        self._line_color_focus = self.line_color_focus
        self._icon_right_color = self.icon_right_color_normal
        self._icon_left_color = self.icon_left_color_normal
        self._max_length_text_color = [0, 0, 0, 0]
        self._helper_text_color = [0, 0, 0, 0]

    @staticmethod
    def format_rut(value):
        clean = ''.join(c for c in value if c.isdigit() or c in 'kK')[:9]
        if len(clean) <= 1:
            return clean.upper()
        body, dv = clean[:-1], clean[-1].upper()
        out = ''
        for i, ch in enumerate(reversed(body)):
            if i and i % 3 == 0:
                out = '.' + out
            out = ch + out
        return '%s-%s' % (out, dv)

    def set_text(self, instance_text_field, text):
        """
        Reemplaza a set_text() de MDTextField (que KivyMD enlaza al cambiar
        el texto). A proposito NO se llama a super(): la version de Material
        valida el campo, lo marca en rojo y anima el hint flotante hacia el
        borde superior. Este diseno trae su propio marcador de posicion
        centrado y su propio indicador de validez (el check azul), asi que
        esa maquinaria sobra — y entra en recursion al reformatear aqui
        el texto.
        """
        if self._busy:
            return
        self._busy = True
        formatted = self.format_rut(text)
        if formatted != text:
            self.text = formatted
            self.cursor = (len(formatted), 0)
        clean = formatted.replace('.', '').replace('-', '')
        self.valid = None if not clean else len(clean) >= 8
        self.dispatch('on_rut_valid', self.valid)
        self._busy = False


# ========================================================== LIENZO DE FIRMA
class SignaturePad(StencilView):
    """
    Area donde se dibuja la firma con el mouse o el dedo.
    Dispara on_signature_change(bool) — enlazable desde .kv.
    Solo visual: el trazo no se exporta ni se guarda.
    """
    def __init__(self, **kw):
        super().__init__(**kw)
        self._line = None
        self.has_signature = False
        self.register_event_type('on_signature_change')

    def on_signature_change(self, has_signature):
        pass

    def clear(self):
        self.canvas.clear()
        self._line = None
        self.has_signature = False
        self.dispatch('on_signature_change', False)

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        with self.canvas:
            Color(*T.C_TEXT)
            self._line = Line(points=[touch.x, touch.y], width=dp(1.3),
                              cap='round', joint='round')
        if not self.has_signature:
            self.has_signature = True
            self.dispatch('on_signature_change', True)
        touch.grab(self)
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is self and self._line is not None:
            self._line.points += [touch.x, touch.y]
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self._line = None
            return True
        return super().on_touch_up(touch)

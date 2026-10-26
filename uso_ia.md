# Declaración de uso de IA

Este documento registra el uso de inteligencia artificial en el desarrollo de
**FirmApp**, tal como lo pide el instrumento de evaluación **E2 — TINF1119
(Desarrollo Móvil A+S)**: "README.md con... declaración de uso de IA (si
aplica)".

- **Herramienta:** Claude Code (Anthropic), modelos Claude Opus 5.5 y Claude
  Sonnet 5, en una sesión de ejecución en la nube sobre este repositorio.
- **Fecha:** 28 de septiembre de 2026.
- **Conversación de referencia:** el estudiante compartió además un enlace a
  un chat previo de Claude sobre este mismo tema
  (`https://claude.ai/share/00e8712d-cca6-41f9-8cd7-cee73b506069`); el
  contenido de esa conversación no pudo recuperarse desde esta sesión (el
  enlace no expuso su contenido a una herramienta automática de lectura), por
  lo que este documento registra lo efectivamente pedido y hecho **en esta
  sesión**, que es la que realizó los cambios de código.
- **Sesión de esta ejecución (trazabilidad técnica):**
  `https://claude.ai/code/session_01KBjmqzBqPJ2Hs1HFW63rQu`

## Qué se le pidió a la IA (en orden)

1. **"Analiza el proyecto entero."** Revisión completa del repositorio
   (`main.py`, `widgets.py`, `theme.py`, `icons.py`, `interfazrrhh.kv`,
   `README.md`, `requirements.txt`), incluyendo ejecutar la app en un entorno
   sin pantalla (Xvfb) para verificar comportamiento real, no solo lectura de
   código.
2. **Aplicar las correcciones propuestas en ese análisis**, además de:
   - agregar esta declaración de uso de IA (`uso_ia.md`),
   - identificar si el proyecto usa `ScreenManager`,
   - revisar la rúbrica de evaluación (`.docx` adjunto) y hacer los cambios
     necesarios para cumplir sus requisitos.
3. **"Revisa y analiza todo el repositorio y comprueba que todo esté bien"**
   (tras fusionarse el PR #1 a `main` y renombrarse la rama) — verificación
   de que el merge no rompió nada: sin marcadores de conflicto, archivos
   `.py`/`.kv` compilan, y la app recorre las 3 pantallas sin errores.
4. **"Incluye este archivo [`FUNDAMENTACION-UX-UI.md`] y actualiza todo en
   el repositorio"** — incorporar el documento de fundamentación UX/UI que
   el estudiante redactó con su propia investigación, y actualizar
   `README.md` y este archivo para reflejarlo (ver sección "Actualización —
   `FUNDAMENTACION-UX-UI.md`" más abajo).
5. **"Ajusta el texto del documento y describe lo que sí hace. En caso de
   que veas otra inconsistencia realiza los cambios necesarios"** —
   corrección de la matriz hallazgo → decisión y de la sección 4 para que
   nombren las pantallas y componentes reales del código (`HomeScreen`,
   `SignScreen`, `SuccessScreen`, `SolidButton`/`MDCard`), sin alterar
   ningún dato de la investigación del estudiante.
6. **"Vuelve a hacer el diseño de antes de las pantallas, implementa Remote
   Config (con el PDF de la Sesión 22 como guía), encárgate de
   notificaciones/alertas y Remote Config (no de JSON/persistencia, de eso
   se encarga mi compañero), explica los cambios, y dime cómo subirlo al
   repositorio para que mi compañero y el profesor puedan clonarlo sin
   dificultad."** Ver sección "Actualización — Evaluación N°3" más abajo.
7. **"Implementa un login, manteniendo el diseño de la app en general, el
   login debe verificar que sea un rut válido o en su defecto un correo
   (con el formato, es decir nombre@gmail.com). Actualiza también el
   archivo de uso_ia.md con todos los cambios nuevos y solicitados."** Ver
   sección "Actualización — Pantalla de Login" más abajo.
8. **"Actualiza FUNDAMENTACION-UX-UI.md. ¿Debo hacer clone de nuevo? ¿Cómo
   actualizo el archivo en mi Visual?"** y, en mensajes separados, 4 rondas
   de ajustes visuales/funcionales sobre el Login a partir de capturas
   reales (centrado, tamaño de letra, puntos de la contraseña, el botón
   "Ingresar" que no se habilitaba, y el bug real de no poder escribir un
   correo) — ver sección "Actualización — Ajustes de la pantalla de Login"
   más abajo.
9. **"El apartado de la notificación debe ser más llamativo... que al
   presionar [la campana] aparezca la notificación en grande."** Ver
   sección "Actualización — Banner y campana de notificaciones" más abajo.

## Qué encontró el análisis inicial

- El repositorio tenía versionado el entorno virtual `.venv/` completo (de
  Windows, 130 MB, 5.276 de los 5.291 archivos del repo), `__pycache__/` y
  dos `.zip` de fuentes redundantes; no existía `.gitignore`.
- `requirements.txt` solo tenía `kivy>=2.3.0` y le faltaba `kivymd`, pese a
  que toda la app depende de KivyMD 1.2.0.
- `theme.py` buscaba `DMSans-Regular.ttf` / `DMSans-Bold.ttf`, pero los
  archivos reales en `assets/fonts/` se llaman
  `DMSans_18pt-Regular.ttf` / `DMSans_18pt-Bold.ttf` → la app nunca cargaba
  DM Sans y usaba Roboto en silencio.
- Al cambiar de pestaña (RUT ↔ Dibujar Firma) y volver, el botón "Firmar con
  1 toque" quedaba habilitado aunque el campo/lienzo estuviera vacío de
  nuevo (el estado `_rut_valid` / `_has_signature` no se reiniciaba).
- `Pressable` (`widgets.py`) hacía `Window.bind(mouse_pos=...)` sin
  desconectarlo nunca: cada apertura del modal de firma dejaba listeners
  colgados en memoria.
- Al firmar, la pantalla de éxito solo ponía `opacity = 0` a la cabecera y
  las pestañas del modal, pero esos botones seguían recibiendo toques
  (invisibles pero clicables) detrás del mensaje de éxito.
- **No existía `ScreenManager`**: toda la app era una sola pantalla
  (`RootScreen`) con un modal (`ModalOverlay` + `SignatureModal`) superpuesto
  mediante `add_widget`/`remove_widget`, no navegación real entre pantallas.
- El botón "Firmar sin sesión" de `FooterCard`/`DesktopCtaCard` asumía que
  `PENDING` nunca estaría vacía (`PENDING[0]` sin verificar longitud).

## Qué se cambió en el código

### Limpieza de repositorio
- Se creó `.gitignore` (`.venv/`, `__pycache__/`, `*.pyc`, `*.zip`, etc.).
- Se quitaron del control de versiones y del disco `.venv/`, `__pycache__/`
  y los `.zip` de fuentes ya redundantes con los `.ttf` extraídos.
- `requirements.txt` ahora fija `kivy==2.3.1` y `kivymd==1.2.0` (las
  versiones que el propio `.kv` y el `README` exigen).

### Corrección de bugs
- `theme.py`: nombres de fuente corregidos a los archivos reales
  (`DMSans_18pt-Regular.ttf`, `DMSans_18pt-Bold.ttf`).
- `widgets.py` (`Pressable`): se agregó `on_parent()` para desconectar
  `Window.unbind(mouse_pos=...)` cuando el widget sale del árbol, evitando
  la fuga de memoria.
- `main.py` (`FooterCard`/`DesktopCtaCard.sign_pressed`): se agregó un
  chequeo de `PENDING` vacía antes de indexar `PENDING[0]`.

### Reestructuración a `ScreenManager` (requisito C2 de la rúbrica)
Se reemplazó el modal superpuesto por **3 pantallas navegables** con
`kivy.uix.screenmanager.ScreenManager`, creadas una sola vez en
`InterfazRRHHApp.build()`:

1. `HomeScreen` (`name='home'`) — envuelve el tablero existente
   (`RootScreen`) sin cambiar su lógica.
2. `SignScreen` (`name='sign'`) — aloja `SignPanel` (antes
   `SignatureModal`) con las pestañas RUT / Dibujar Firma.
3. `SuccessScreen` (`name='success'`) — pantalla de confirmación, con botón
   para volver a Inicio.

La navegación (`InterfazRRHHApp.go_to_sign`, `.go_to_success`, `.go_home`)
solo cambia `sm.current` con `SlideTransition`, sin crear ni destruir
widgets en cada viaje. Este cambio, además de cumplir el requisito técnico
de la evaluación, **corrigió de raíz** dos de los bugs encontrados:
- el estado de validación ya se reinicia explícitamente en
  `SignPanel.set_tab()` y en `SignPanel.reset_for()` (llamado cada vez que
  se entra a `SignScreen` con un documento nuevo);
- ya no queda ningún botón "invisible pero clicable" en la pantalla de
  éxito, porque ahora es una `Screen` distinta, no una superposición de
  opacidad sobre el mismo widget.

Se verificó el resultado ejecutando la app en un entorno sin pantalla
(Xvfb) con un script de prueba que recorre las 3 pantallas, fuerza el
cambio de pestañas, firma y vuelve a Inicio varias veces seguidas,
comprobando que el botón CTA se deshabilita correctamente al cambiar de
pestaña y que el número de listeners de `mouse_pos` no crece tras varios
ciclos de navegación. Se tomaron capturas reales de las 4 pantallas
(Inicio, Firmar-RUT, Firmar-Dibujo, Éxito) y se agregaron a
`assets/screenshots/` y al `README.md`.

### `README.md`
Se completó con las secciones que exige la rúbrica y que faltaban:
"Problema que resuelve", "Usuario objetivo", "Capturas de pantalla" y esta
"Declaración de uso de IA" (enlazando a este archivo). También se actualizó
la sección de estructura de archivos y se agregó la sección "Navegación
(ScreenManager)".

## Actualización — `FUNDAMENTACION-UX-UI.md` (commit "Archivo fundamentacion ux-ui")

En una sesión posterior, el estudiante entregó el documento
`FUNDAMENTACION-UX-UI.md` ya redactado, con su propia investigación
(encuesta de diagnóstico en Google Forms, 11 respuestas). La IA **no generó
ni modificó ese contenido**: solo lo incorporó al repositorio tal como se
entregó (`git add` + commit) y actualizó las referencias cruzadas en
`README.md` (sección "Fundamentación UX/UI" y estructura de archivos) para
enlazarlo.

Al incorporarlo se detectó una inconsistencia entre el documento y el
código: la matriz hallazgo → decisión (sección 3) y la justificación de
navegación (sección 4) nombraban pantallas `PantallaInicio`,
`PantallaFormulario` y `PantallaEstado`, que no existen — las clases reales
en `main.py`/`interfazrrhh.kv` son `HomeScreen`, `SignScreen` y
`SuccessScreen`. Además, `PantallaFormulario` describía un formulario de
solicitud de permisos/vacaciones que no está implementado como pantalla
navegable (las tarjetas "Pedir Vacaciones" y "Solicitar Permiso" del
Dashboard hoy no tienen acción asociada).

**A pedido explícito del estudiante** ("ajusta el texto del documento y
describe lo que sí hace"), la IA reescribió las filas H1, H4 y H5 de la
matriz, la sección 4 completa (con los nombres reales de pantalla y el
flujo Inicio → Firmar → Éxito) y la mención de `MDButton`/`MDCard` de la
sección 5 (la app usa `SolidButton`/`PressCard` sobre `MDCard`, no
`MDButton`) — **sin tocar ningún dato de la investigación** (porcentajes,
recuentos, ficha técnica de la muestra, hallazgos 1–5 de la sección 2):
solo se reescribió cómo se describe la implementación en Kivy/KivyMD, para
que trace decisiones que sí existen en el código. Se agregó además una nota
explícita en la matriz (bajo H4) aclarando que el formulario de
permisos/vacaciones aún no está implementado y por qué, en vez de fingir
que existe.

## Qué revisó la IA de la rúbrica y no alcanzó a resolver

- Criterio A (Fundamentación UX/UI, 30 pts): documento presente y ya
  alineado con el código (ver actualización arriba). La investigación en sí
  (metodología, hallazgos, cifras) es responsabilidad del estudiante; la IA
  no la generó ni la alteró.
- Criterio D (presentación oral, 15 pts): no aplica a un cambio de código;
  es responsabilidad del estudiante al exponer.

## Actualización — Evaluación N°3: efecto visual, Remote Config y Notificaciones

El estudiante compartió la rúbrica de la **Evaluación N°3** (Proyecto
Práctico N°2: Diseño y estructura app Kivy) y la diapositiva de la
**Sesión 22** (Remote Config, Notificaciones con Plyer), y pidió 3 cosas:

1. **Recuperar el efecto visual de la v1** (modal flotante sobre el
   Dashboard oscurecido) para `SignScreen`/`SuccessScreen`, que se había
   perdido al convertirlas en pantallas de `ScreenManager` a toda pantalla.
2. **Implementar Remote Config y Notificaciones** (los otros dos pilares —
   persistencia JSON y autenticación — quedan fuera, a cargo de otro
   integrante del equipo).
3. Explicar los cambios y dejar instrucciones claras de Git para que el
   equipo y el docente puedan clonar y ejecutar sin dificultades.

Antes de tocar código se le preguntó explícitamente al estudiante (con el
mecanismo de pregunta al usuario de Claude Code, no asumiendo) qué tan
atrás quería revertir, porque la propia diapositiva de la Sesión 22 da por
hecho que las rutas de `ScreenManager` ya existen ("Código Local
(Estructural)" en la matriz de decisión de arquitectura) — es decir,
deshacer el `ScreenManager` por completo habría contradicho el material de
la propia sesión. Se acordó: mantener las 3 pantallas, pero reconstruir el
efecto visual de modal flotante.

### Efecto visual (sin volver al modal con fuga de memoria)

`InterfazRRHHApp._snapshot_home()` toma una foto del Dashboard
(`Widget.export_as_image()`) justo antes de navegar a Firmar, y
`SnapshotBackground` (clase nueva en `widgets.py`) la pinta de fondo con un
velo oscuro encima. **Se descartó deliberadamente** usar el widget `Image`
de Kivy para esto: en las pruebas (ver abajo) se asignó `.texture`
directamente y la imagen se renderizaba diminuta y mal ubicada, porque
`Image` depende de cargar su textura a través de `source` para calcular
correctamente su tamaño de render (`norm_image_size`). Se resolvió
dibujando la textura a mano con `kivy.graphics.Rectangle`, el mismo patrón
que ya usaba `MeshBackground` en este proyecto. También se detectó (y
corrigió) que la textura de un `Fbo`/`export_as_image()` sale con el eje Y
invertido en Kivy — se corrige una sola vez con `texture.flip_vertical()`
en el punto de captura.

### Remote Config (`remote_config.py` + `remote/config.json`)

Sigue el patrón exacto de la diapositiva "Flujo Seguro y Resiliencia de
Red": Default Local → Fetch Asíncrono (`UrlRequest`, no bloquea la UI) →
Activate (si el JSON llega bien) o Fallback (si no hay red o falla, la app
sigue con los valores locales sin interrumpir). Controla 3 parámetros:
`banner_message` (texto), `show_desktop_cta` (feature flag) y
`max_recent_docs` (límite numérico) — los mismos 3 tipos de ejemplo de la
diapositiva.

**El JSON no se alojó en un GitHub Gist** como sugiere la diapositiva:
se intentó crear uno con la API de GitHub (`gh api -X POST gists`) y el
proxy de esta sesión lo rechazó explícitamente (`403: Gist writes are not
permitted through this proxy`). Se le avisó al estudiante y, con su
aprobación, se usó la alternativa ya ofrecida de antemano: `remote/config.json`
dentro del propio repositorio, servido vía la URL "raw" de GitHub
(`raw.githubusercontent.com`) — cumple el mismo patrón cliente/servidor
remoto sobre HTTP real, y además sirve para la "Modificación en vivo" de la
defensa (criterio 4 de la rúbrica): basta editar ese archivo, hacer commit
y push, sin tocar el código Python.

### Notificaciones (`notifications.py`, Plyer)

Envuelve `plyer.notification.notify()` en un `try/except` — una
notificación nunca debe tumbar la app. Se dispara al abrir la app (si hay
un documento urgente pendiente) y al firmar con éxito. Se agregó `plyer` a
`requirements.txt`.

### Cómo se probó

Todo (snapshot del Dashboard, textura, velo oscuro, transición, Remote
Config con fallback real porque `remote/config.json` todavía no estaba
publicado en GitHub al momento de la prueba, y notificaciones) se corrió en
un entorno sin pantalla (Xvfb), con capturas de pantalla reales en cada
paso, antes de darlo por terminado. La falla de notificaciones en ese
entorno (`No usable implementation found!`, por no tener `dbus`/
`notify-send` instalados en el contenedor Linux) es esperada y no indica un
problema de la app: en Windows, Plyer usa un backend nativo distinto
(notificación de barra de tareas) que si debería funcionar.

## Actualización — Pantalla de Login

El estudiante pidió una pantalla de inicio de sesión, "manteniendo el
diseño de la app en general", que valide un RUT chileno válido o, en su
defecto, un correo con formato `nombre@dominio.com`, y que se dejara
registrado todo en este archivo.

### Dónde quedó cada parte

- **`validators.py`** (nuevo, archivo completo): funciones puras (sin
  nada de Kivy) para validar RUT y correo:
  - `is_valid_rut()` calcula el **dígito verificador real** del RUT
    (algoritmo módulo 11 — cada dígito del cuerpo, de derecha a
    izquierda, se multiplica por un factor de 2 a 7 que vuelve a
    empezar en 2; el DV es 11 menos el resto de esa suma dividida
    por 11). Esto corrige una limitación que ya se había señalado en
    el análisis inicial del proyecto: antes (`RutInput` en la pantalla
    de Firmar) solo se validaba el **largo** del RUT, no el dígito
    verificador — por ejemplo `11.111.111-2` pasaba como válido antes,
    y con esta función no. `RutInput` (la firma de un documento ya
    elegido) se dejó tal cual estaba, sin tocar: la pantalla de Login es
    la que ahora hace la validación real.
  - `is_valid_email()` valida la forma `nombre@dominio.tld` con una
    expresión regular, tal como se pidió explícitamente
    ("con el formato, es decir nombre@gmail.com").
  - `identify()` combina ambas: si el texto tiene `@` lo trata como
    correo, si no, como RUT.
  - Se probaron a mano con RUTs de prueba conocidos (`12345678-5`,
    `11.111.111-1`, `7654321-6` válidos; `11.111.111-2` inválido) y
    varios correos válidos/inválidos antes de usarlas en la interfaz.
- **`widgets.py`**: dos clases nuevas, `LoginIdentifierInput` (el campo
  único que acepta RUT o correo, se autoformatea como RUT mientras no
  tenga `@`, y llama a `validators.identify()` en cada tecla) y
  `PasswordInput` (campo de contraseña enmascarado, sin validación real
  — solo necesita no estar vacío).
- **`main.py`**: `LoginScreen` (nueva pantalla del `ScreenManager`,
  ahora la primera que se muestra al abrir la app) habilita el botón
  "Ingresar" solo cuando el identificador es válido y la contraseña
  tiene 4+ caracteres. `login()` navega a Inicio — es una maqueta, no
  hay backend que autentique nada de verdad, tal como el resto del
  proyecto; se dejó un comentario explícito en el código marcando ese
  método como el punto exacto donde conectar una autenticación real.
- **`interfazrrhh.kv`**: regla `<LoginScreen>:` nueva, con el mismo
  lenguaje visual que el resto de la app (`GlassCard` sobre
  `MeshBackground`, recuadros redondeados propios en vez de los de
  Material, el mismo patrón de check verde que ya usaba la pestaña de
  RUT en Firmar) — cumpliendo el pedido de "mantener el diseño de la
  app en general".

### Un bug real que se encontró y corrigió probando

Al probar la pantalla, el texto "RUT detectado"/"Correo detectado" se
quedaba congelado con su primer valor aunque el usuario siguiera
escribiendo. La causa: `kind` y `valid` en `LoginIdentifierInput`
se habían escrito como atributos Python comunes (`self.kind = None`),
no como `Property` de Kivy -- y el `.kv` no puede reaccionar de forma
confiable a cambios en algo que no es una `Property` observable. Se
corrigió convirtiéndolas en `StringProperty`/`BooleanProperty` reales.
Se verificó con un script que inspecciona el widget directamente (no solo
mirando capturas de pantalla) que el texto ya cambia correctamente al
escribir.

### Cómo se probó

En el mismo entorno sin pantalla (Xvfb) usado para el resto del proyecto:
escribir un RUT con dígito verificador incorrecto (botón sigue
deshabilitado), corregirlo a uno válido (aparece el check y "RUT
detectado"), agregar una contraseña (se habilita "Ingresar"), borrar y
escribir un correo válido (cambia a "Correo detectado"), y presionar
"Ingresar" (navega a Inicio). Después se corrió el flujo completo de
punta a punta: Login → Inicio → Firmar → Éxito → Inicio, para confirmar
que agregar el Login no rompió nada de lo anterior.

### Qué queda fuera, a propósito

Esta pantalla **valida formato**, no identidad: no hay backend, no hay
usuarios reales, cualquier RUT con dígito verificador correcto o
cualquier correo con forma válida "inicia sesión". Eso es justamente lo
que el estudiante pidió que quedara fuera (persistencia/autenticación
real, a cargo de su compañero). `LoginScreen.login()` queda documentado
en el código como el lugar exacto para conectar eso despues.

## Actualización — Ajustes de la pantalla de Login (varias rondas)

Tras ver capturas reales de la app corriendo en Windows, el estudiante
pidió varias correcciones seguidas sobre el Login. Se documentan juntas
porque cada una llevó a encontrar la siguiente:

1. **"El apartado de rut/email está mal centrado, los puntos de la
   contraseña más marcados y grandes, la tipografía más grande."**
   Se subió el tamaño de fuente de ambos campos y se probó primero un
   carácter de contraseña tipo círculo relleno (`●`, U+25CF) — se
   verificó con la librería `fonttools` que la fuente DM Sans **no**
   incluye ese glifo (se veía como un recuadro vacío) y se cambió a
   asterisco (`*`), que sí está en la fuente.
2. **"Sigue sin escribir a la izquierda" / no dejaba presionar
   "Ingresar".** Se intentó centrar el texto (`halign: 'center'`), pero
   resultó frágil: en cuanto el texto se acercaba al ancho del campo,
   Kivy deja de centrar y sigue al cursor, empujando el texto a la
   derecha. Se cambió a `halign: 'left'`. Sobre el botón: se verificó
   con `validators.py` que el RUT de prueba usado por el estudiante
   (`13.213.123-2`, luego `21.123.131-3`) **no era válido de verdad**
   (dígito verificador incorrecto) — no era un bug, era la validación
   funcionando. Se dejaron RUTs de prueba válidos en la respuesta al
   estudiante.
3. **Seguía sin verse bien alineado.** Se encontró la causa real
   inspeccionando el ancho del widget en vivo: el placeholder y el campo
   de texto estaban como hijos directos de un `MDBoxLayout` (que
   **reparte** el ancho entre sus hijos), no de un `MDFloatLayout` (que
   los **superpone**) — el campo de escritura real solo ocupaba la mitad
   derecha de la caja. Se agregó el `MDFloatLayout` intermedio que
   faltaba, el mismo patrón que ya usa el campo de RUT de la pantalla de
   Firmar.
4. **"Que me permita ingresar un correo o un rut, el botón no
   funciona."** Bug real y serio, encontrado al simular tecleo
   caracter-por-caracter con `insert_text()` (como escribe Kivy de
   verdad) en vez de asignar `.text` de una sola vez (como se había
   probado antes, por lo que no se había detectado): el autoformateo de
   RUT borraba cada letra de un correo apenas se escribía, porque
   `format_rut()` descarta todo lo que no sea dígito o "K", y el campo
   lo aplicaba a cualquier texto sin "@" — incluida la parte local de un
   correo mientras el usuario todavía no llegaba al "@". Se corrigió
   para que el autoformateo de RUT solo se aplique si **todo** lo
   escrito hasta ese momento podría ser parte de un RUT. También se
   cambió el mensaje "RUT detectado"/"Correo detectado" (ambiguo, no
   decía si era válido) por "RUT válido"/"RUT inválido: revisa el
   dígito verificador" (y su equivalente para correo).

## Actualización — Banner y campana de notificaciones

El estudiante pidió que el banner de Remote Config fuera "más llamativo"
y que el ícono de campana del encabezado (hasta ahora decorativo)
mostrara la notificación "en grande" al presionarlo.

- `interfazrrhh.kv`: el banner cambió de un tinte celeste sutil a un
  estilo naranja con borde, ícono en una insignia con degradado y una
  flecha (`chevron`) indicando que es presionable — mismo lenguaje que
  la etiqueta "Urgente" ya usada en las tarjetas pendientes.
- `widgets.py`: nueva clase `PressableBox` (`Pressable` + `MDBoxLayout`)
  para que el banner reaccione al toque igual que las tarjetas
  (`PressCard`), sin la sombra/fondo de vidrio que trae `GlassCard`.
- `main.py`: nueva clase `NotificationOverlay` — una superposición
  liviana (no una `Screen` del `ScreenManager`, porque es informativa y
  transitoria, no parte de la navegación) que muestra el mensaje del
  banner en grande y, si hay documentos urgentes, cuántos. La abren
  tanto el ícono de campana como el propio banner
  (`InterfazRRHHApp.show_notifications()`/`hide_notifications()`).
  Deliberadamente se reutilizó el patrón "modal con fondo oscuro" de la
  v1 (`ModalOverlay`original, que se había quitado al pasar a
  `ScreenManager`) porque aquí sí tiene sentido: es un aviso puntual, no
  un paso del flujo de navegación. No reintroduce la fuga de memoria que
  tenía el `ModalOverlay` original, porque `Pressable` (`widgets.py`) ya
  desconecta su listener de `Window` al salir del árbol de widgets (fix
  aplicado en la sesión de Remote Config/Notificaciones).

Probado en el entorno sin pantalla (Xvfb): abrir con la campana, abrir
tocando el banner, cerrar con el botón "Cerrar", y confirmado que
`app.notification_overlay` queda en `None` después de cerrar (para que
`show_notifications()` pueda volver a abrirlo).

## Cómo se usó el resultado

Todo el código generado por la IA fue revisado, ejecutado y probado en este
mismo proceso antes de darlo por válido (ver "Reestructuración a
`ScreenManager`", "Actualización — Evaluación N°3" y "Actualización —
Pantalla de Login" arriba). El estudiante es responsable de revisar el
diff final, entender los cambios y poder explicarlos en la presentación
oral, como exige la rúbrica (D2/criterio 1 — "Fundamentación al exponer" /
"Defensa del código").

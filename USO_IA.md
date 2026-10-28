# Declaración de Uso de IA — FirmApp

Esta declaración sigue la estructura de 6 secciones exigida por la
Evaluación N°3 (TINF1119 — Desarrollo Móvil, Instituto Tecnológico UC
Temuco). Un registro cronológico detallado, con cada commit y cada bug
encontrado, está en el **Anexo** al final de este archivo.

---

## 1. IA usada

Sí se usó inteligencia artificial: **Claude Code**, el agente de línea de
comandos de Anthropic, en una sesión de ejecución en la nube conectada
directamente a este repositorio de GitHub (push y pull reales, no copiar
y pegar código a mano).

## 2. Modelo

**Claude Opus 5.5** y **Claude Sonnet 5** (Anthropic). La sesión cambió de
modelo a mitad de camino (de Opus 5.5 a Sonnet 5) por una acción del
propio estudiante (`/model claude-sonnet-5`), documentada en el historial
de la conversación.

## 3. Prompts realizados

Resumen fiel, en orden, de los pedidos relevantes que explican decisiones
del proyecto (la lista completa, con más contexto de cada uno, está en el
Anexo):

1. *"Analiza el proyecto entero"* — primer pedido, antes de cualquier
   cambio: revisión completa del código existente (una maqueta de Kivy
   sin pantallas, sin backend, con varios bugs).
2. *"Aplica las correcciones propuestas"* + agregar declaración de uso de
   IA + revisar si el proyecto usa `ScreenManager` + revisar la rúbrica
   de una evaluación anterior (E2) y cumplir sus requisitos.
3. *"Revisa y analiza todo el repositorio y comprueba que todo esté
   bien"* — verificación tras fusionar un PR y renombrar la rama.
4. Incorporar un documento de fundamentación UX/UI que el estudiante
   redactó con su propia investigación (encuesta real a 11 personas), y
   actualizar el resto del repositorio para que lo referencie.
5. *"Ajusta el texto del documento y describe lo que sí hace"* — corregir
   la fundamentación UX/UI para que coincida con el código real.
6. *"Vuelve a hacer el diseño de antes de las pantallas, implementa
   Remote Config, encárgate de notificaciones/alertas y Remote Config (no
   de JSON/persistencia, de eso se encarga mi compañero)"* — primera
   implementación de Remote Config y Notificaciones, y restauración del
   efecto visual "modal flotante" de la versión original.
7. *"Implementa un login, manteniendo el diseño de la app en general, el
   login debe verificar que sea un RUT válido o en su defecto un correo
   (con el formato, es decir nombre@gmail.com)"* — primera versión de la
   pantalla de Login (solo validación de **formato**, sin backend, tal
   como se había acotado en el punto 6).
8. Cuatro rondas de ajustes al Login, cada una a partir de una **captura
   de pantalla real** enviada por el estudiante tras probar la app en su
   propio computador con Windows: centrado del campo, tamaño de letra,
   puntos de la contraseña, y un bug real donde no se podía escribir un
   correo.
9. *"El apartado de la notificación debe ser más llamativo... que al
   presionar la campana aparezca la notificación en grande"* — campana
   funcional y banner rediseñado.
10. *"El proyecto [debe implementar] lo que se solicita en el archivo de
    text-to-markdown para la evaluación... debe cumplir con todos los
    puntos"* (pedido final, con la rúbrica oficial de la Evaluación N°3 y
    la diapositiva de la Sesión 24 adjuntas) — esto **cambió el alcance**
    del punto 6: la rúbrica exige explícitamente "Autenticación de
    usuarios: registro y login" y "Persistencia de datos en JSON", que
    antes se habían dejado fuera a pedido del estudiante (reservadas
    para un compañero de equipo). Se implementaron ambas, más una
    revisión completa de `README.md` y la creación de `USO_IA.md` con la
    estructura de 6 secciones exigida.

## 4. Outputs

Lo que entregó la IA, en código real y verificado ejecutando la app (no
solo generado y asumido):

- Reestructuración completa a `ScreenManager` con pantallas reales
  (`HomeScreen`, `SignScreen`, `SuccessScreen`, y luego `LoginScreen` y
  `RegisterScreen`), reemplazando un modal superpuesto que tenía una fuga
  de memoria real (un listener de `Window` nunca desconectado).
- `remote_config.py` y `notifications.py`: Remote Config (con fallback
  seguro) y notificaciones locales con Plyer.
- `validators.py`: validación de RUT chileno con dígito verificador real
  (algoritmo módulo 11) y de formato de correo.
- `data_manager.py`: persistencia en JSON de cuentas de usuario
  (contraseña con hash SHA-256) y del estado de los documentos
  (pendientes/firmados), con manejo de excepciones en cada lectura y
  escritura.
- Corrección de bugs reales encontrados **probando la app**, no solo
  leyendo el código: una fuga de memoria, un widget `Image` que
  renderizaba una textura mal (diminuta y mal ubicada), un `MDBoxLayout`
  que repartía el ancho de un campo en vez de superponerlo, un
  autoformateo de RUT que borraba las letras de un correo mientras se
  escribía, y una respuesta HTTP que Kivy no decodificaba como JSON por
  el `Content-Type` que manda GitHub.
- `README.md`, `FUNDAMENTACION-UX-UI.md` y este mismo `USO_IA.md`,
  actualizados en cada etapa.

**Qué se descartó:**
- Un carácter de contraseña tipo círculo relleno (●, U+25CF) para
  enmascarar la contraseña: se verificó con la librería `fonttools` que
  la fuente del proyecto (DM Sans) no lo incluye — se veía como un
  recuadro vacío. Se usó un punto (•, U+2022), que sí está en la fuente.
- Alojar el JSON de Remote Config en un GitHub Gist (como sugiere el
  material del curso): la API de GitHub lo rechazó por una política del
  entorno de desarrollo usado. Se sirvió desde el propio repositorio en
  su lugar (`raw.githubusercontent.com`), que cumple el mismo patrón.
- Texto centrado para el campo de RUT/correo del Login: se abandonó por
  frágil (Kivy deja de centrar y sigue al cursor una vez que el texto no
  cabe) a favor de texto alineado a la izquierda, el estándar de
  cualquier campo de formulario.

## 5. Ajustes

Esta es la sección que más importa, y donde está la diferencia entre usar
una herramienta y delegarle el trabajo:

- **El estudiante acotó el alcance en cada etapa**, no la IA: decidió
  explícitamente qué partes le tocaban a él (Remote Config,
  Notificaciones, y más tarde Login/Persistencia) y cuáles a su
  compañero de equipo (persistencia/autenticación, al principio). Cuando
  la rúbrica final exigió que el repositorio individual cumpliera con
  *todos* los puntos, el estudiante lo señaló explícitamente y se
  implementó lo que faltaba.
- **El estudiante tomó la decisión de arquitectura clave**, no la IA: al
  pedir "volver al diseño de antes", la IA le hizo notar que la propia
  diapositiva del curso asumía que `ScreenManager` ya existía (listaba
  sus rutas como "código local" sobre el que se construye el resto), y
  le preguntó explícitamente qué tan atrás quería revertir. El
  estudiante decidió mantener la navegación y solo recuperar el efecto
  visual.
- **El estudiante encontró bugs reales probando la app en su propio
  computador**, no solo leyendo el código generado: el campo de
  RUT/correo mal alineado, los puntos de la contraseña poco visibles, y
  el bug donde no se podía escribir un correo — los tres se detectaron
  porque el estudiante mandó capturas de pantalla reales de Windows, no
  porque la IA los encontrara sola. Esas capturas forzaron a diagnosticar
  la causa real cada vez (por ejemplo, el problema de alineación no era
  de estilo sino de qué tipo de layout envolvía los campos).
- **El estudiante definió los requisitos de validación exactos**: "RUT
  válido o en su defecto un correo (con el formato, es decir
  nombre@gmail.com)" — la IA no decidió qué constituye un RUT o un correo
  válido, el estudiante lo especificó.
- **Convenciones del repositorio pedidas explícitamente**: el nombre
  exacto de este archivo (`USO_IA.md`, en mayúsculas, no `uso_ia.md`
  como se había usado antes) se ajustó porque la rúbrica lo exige así.

## 6. Reflexión en el uso de IA

> **Nota para quien lea esto en la defensa:** esta sección debe ser la
> reflexión genuina del estudiante, en su propia voz — no se puede
> declarar como propia una reflexión que escribió la IA. Lo que sigue es
> un **borrador de partida** con la estructura que pide la pauta (qué
> sirvió, qué costó, qué se aprendió); está pensado para que el
> estudiante lo reemplace o lo edite con lo que realmente vivió antes de
> entregar, no para presentarlo tal cual.

*(Borrador — reemplazar antes de entregar)*

Usar IA para este proyecto sirvió sobre todo para moverme rápido en la
parte de Kivy que menos domino — el `.kv` tiene comportamientos que no
son intuitivos (por qué un `BoxLayout` reparte el ancho en vez de
superponer, por qué `Image` no renderiza bien una textura asignada a
mano) y hubiera tardado mucho más en encontrar esas causas por mi cuenta.
Lo que más me costó fue justamente no quedarme con la primera respuesta:
varias veces la implementación se veía bien en las pruebas automáticas
pero al correrla yo en mi computador se notaba un problema real (el
campo de texto mal alineado, la contraseña ilegible) que solo yo podía
ver porque soy quien realmente usa la app en Windows. Aprendí que probar
con capturas de pantalla propias, no solo confiar en que "compila y pasa
los tests", es necesario incluso cuando se usa una herramienta que
también prueba su propio código. También aprendí [completar: algo
específico del proyecto — por ejemplo, el algoritmo del dígito
verificador del RUT, cómo funciona el flujo asíncrono de `UrlRequest`,
o la diferencia entre persistencia local y un backend real].

---

## Anexo — Registro cronológico detallado

*(Para quien quiera el detalle completo de cada cambio, commit y bug
encontrado, con el razonamiento técnico de cada decisión.)*

### Qué encontró el análisis inicial (antes de cualquier cambio)

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
  nuevo.
- `Pressable` (`widgets.py`) hacía `Window.bind(mouse_pos=...)` sin
  desconectarlo nunca: cada apertura del modal de firma original dejaba
  listeners colgados en memoria.
- Al firmar, la pantalla de éxito solo ponía `opacity = 0` a la cabecera y
  las pestañas del modal, pero esos botones seguían recibiendo toques
  detrás del mensaje de éxito.
- **No existía `ScreenManager`**: toda la app era una sola pantalla
  (`RootScreen`) con un modal (`ModalOverlay` + `SignatureModal`) superpuesto
  mediante `add_widget`/`remove_widget`, no navegación real entre pantallas.

### Reestructuración a ScreenManager (Evaluación N°2)

Se reemplazó el modal superpuesto por pantallas navegables con
`kivy.uix.screenmanager.ScreenManager`, creadas una sola vez en
`InterfazRRHHApp.build()`. `SignatureModal` → `SignPanel` (deja de ser un
modal, vive dentro de `SignScreen`). Esto corrigió de raíz dos bugs: el
estado de validez ya no sobrevive al cambiar de pestaña y volver
(`SignPanel.set_tab()`/`reset_for()` lo reinician), y ya no quedan botones
invisibles-pero-clicables detrás de la pantalla de éxito.

### Fundamentación UX/UI

Se incorporó `FUNDAMENTACION-UX-UI.md`, redactado por el estudiante con su
propia investigación (encuesta de diagnóstico real, 11 respuestas). La IA
no generó ni alteró esos datos — solo corrigió, a pedido explícito del
estudiante, que la matriz hallazgo → decisión y la sección de navegación
nombraran las pantallas y componentes reales del código (`HomeScreen`,
`SignScreen`, `SuccessScreen`, luego `LoginScreen`), sin tocar ningún
porcentaje, hallazgo o cita de la investigación.

### Remote Config y Notificaciones (primera implementación)

- `remote_config.py`: patrón Default Local → Fetch Asíncrono (`UrlRequest`)
  → Activate (si el JSON llega bien) o Fallback (si no hay red o falla).
  3 parámetros: `banner_message`, `show_desktop_cta`, `max_recent_docs`.
  El JSON se sirve desde este mismo repositorio
  (`raw.githubusercontent.com`) después de que la API de GitHub rechazó
  crear un Gist por política del entorno de desarrollo.
- Bug real encontrado y corregido: GitHub sirve los `.json` como
  `text/plain`, no `application/json` — `UrlRequest` no lo autodetectaba
  como JSON y lo descartaba como inválido. Se agregó un `json.loads()`
  manual.
- `notifications.py`: envuelve `plyer.notification.notify()` en
  `try/except` — se dispara al detectar un documento urgente y al firmar
  con éxito.
- Efecto visual "modal flotante": se restauró fotografiando el Dashboard
  (`Widget.export_as_image()`) y pintándolo oscurecido detrás de la
  tarjeta de Firmar/Éxito. Bug real: con el widget `Image` de Kivy, la
  foto se veía diminuta y mal ubicada (`Image` no recalcula bien su
  tamaño cuando se le asigna una textura sin pasar por `source`) — se
  corrigió dibujando la textura a mano con `kivy.graphics.Rectangle`
  (`SnapshotBackground` en `widgets.py`). También se corrigió el volteo
  vertical propio de las texturas de `Fbo` (`texture.flip_vertical()`).

### Pantalla de Login (primera versión) y sus ajustes

- `validators.py`: `is_valid_rut()` (dígito verificador real, módulo 11) e
  `is_valid_email()` (formato `nombre@dominio.tld`).
- `LoginIdentifierInput`/`PasswordInput` (`widgets.py`).
- 4 rondas de ajuste a partir de capturas reales de Windows:
  1. Puntos de contraseña más grandes y marcados, tipografía más grande.
     Se probó un carácter de círculo relleno (●) que no estaba en la
     fuente DM Sans (verificado con `fonttools`) — se usó asterisco, y
     después punto (•, que sí está en la fuente).
  2. Centrado frágil (Kivy deja de centrar y sigue al cursor cuando el
     texto no cabe) → se cambió a alineado a la izquierda. Se confirmó
     además que un RUT de prueba del estudiante no era válido de verdad
     (dígito verificador incorrecto) — no era un bug del botón.
  3. El campo seguía mal alineado: la causa real era que el placeholder y
     el campo de texto eran hijos de un `MDBoxLayout` (reparte el ancho)
     en vez de un `MDFloatLayout` (lo superpone) — el campo real solo
     ocupaba la mitad de la caja.
  4. Bug real y serio: el autoformateo de RUT borraba cada letra de un
     correo apenas se escribía, porque descartaba todo lo que no fuera
     dígito o "K" — se detectó simulando tecleo real
     (`insert_text()` carácter por carácter) en vez de asignar el texto
     completo de una vez (como se había probado antes, por lo que no se
     había detectado). Se corrigió para que el autoformateo solo se
     aplique si todo lo escrito hasta ese momento podría ser un RUT.

### Campana y banner de notificaciones

El banner de Remote Config pasó de un tinte celeste sutil a un estilo
naranja presionable (`PressableBox`, nueva clase en `widgets.py`), y el
ícono de campana (antes decorativo) ahora abre `NotificationOverlay`
(`main.py`) con el mensaje en grande — reutilizando el patrón "modal con
fondo oscuro" de la versión original, ya sin su fuga de memoria.

### Evaluación N°3: Autenticación real y Persistencia (este commit)

A partir de la rúbrica oficial de la Evaluación N°3 y la diapositiva de la
Sesión 24 (ambas adjuntadas por el estudiante), se identificó que el
repositorio individual debía cumplir con **todos** los servicios exigidos,
incluidos los que antes se habían acotado como responsabilidad de otro
integrante del equipo:

- `data_manager.py` (`DataManager`): persistencia en JSON de cuentas
  (`data/usuarios.json`, contraseña con hash SHA-256) y de documentos
  (`data/documentos.json`, PENDING/RECENT), con `try/except` en cada
  lectura y escritura.
- `LoginScreen.login()` ahora autentica de verdad contra
  `DataManager.authenticate()` (antes solo validaba formato).
- `RegisterScreen` (nueva pantalla): crea una cuenta con
  `DataManager.register_user()` y entra directo a Inicio.
- `SignPanel.sign()` → `InterfazRRHHApp.complete_signature()`: mueve el
  documento firmado de `PENDING` a `RECENT` y lo persiste — confirmado
  cerrando el proceso de la app y abriendo uno nuevo, verificando que el
  documento firmado ya no aparece como pendiente.
- Cuenta de prueba precargada (`demo@firmapp.cl` / `demo1234`), creada
  sola la primera vez que se abre la app, para no depender de registrarse
  antes de poder hacer la demo.
- Se corrigió además un contador hardcodeado (`count: 2` en el `.kv`, el
  badge de "Tareas Pendientes" y la tarjeta "sin firma") que antes era
  cosmético (`PENDING` nunca cambiaba) y ahora sí importaba: se volvió
  reactivo (`RootScreen.pending_count`).
- `README.md`: se agregó una tabla "Servicios implementados" con la
  ubicación exacta de cada uno, secciones de Registro y Persistencia, y
  una sección de "Dificultades encontradas".
- Este archivo se renombró de `uso_ia.md` a `USO_IA.md` (mayúsculas, como
  exige la rúbrica) y se reestructuró en las 6 secciones de esta pauta.

### Remote Config en tiempo real (sin depender de un `git push`)

Pedido del estudiante: *"el remote config debe ser en tiempo real, sin
tener que hacer push... mientras se ejecuta y modifico el archivo, debe
reflejarse"*. La primera versión solo pedía el JSON remoto **una vez**,
al abrir la app. Se agregó:

- `Clock.schedule_interval()` en `InterfazRRHHApp.build()`: vuelve a
  pedir el mismo valor cada `REMOTE_CONFIG_POLL_INTERVAL` (5 s) mientras
  la app sigue abierta, sin reiniciarla.
- `remote_config.fetch()` ahora acepta, además de una URL `http(s)://`,
  una ruta de archivo local — la lee directo del disco en vez de pedirla
  por red. Esto se agregó porque `raw.githubusercontent.com` (la fuente
  remota real del proyecto) cachea el archivo en su CDN por varios
  minutos tras cada `git push`, lo que hace inviable demostrar un cambio
  "en vivo" en la defensa. Apuntando `REMOTE_CONFIG_URL` al archivo local
  (`remote/config.json`) en vez de a GitHub, el mismo mecanismo de
  polling permite editar ese archivo con la app corriendo y ver el
  cambio reflejado en la pantalla en el siguiente ciclo (máx. 5
  segundos), sin ningún `git push` de por medio — ver `README.md`,
  sección "Remote Config".
- Probado de extremo a extremo en modo headless (Xvfb): se construyó la
  app completa, se confirmó el valor inicial del banner, se editó el
  archivo `remote/config.json` en disco con la app ya corriendo, se
  forzó un ciclo de polling, y se confirmó que `banner_text` y
  `max_recent` del Dashboard cambiaron al nuevo valor sin reiniciar el
  proceso.

### Revisión general y correcciones

A pedido del estudiante ("dale una vuelta al proyecto"), la IA revisó el
código, lo ejecutó en modo headless y reportó los problemas antes de
tocar nada; el estudiante aprobó los cambios (sí/no) uno a uno:

- Remote Config se caía con valores mal tipeados (`"3"`, `null`) y el
  polling reconstruía las listas cada 5 s aunque no hubiera cambios: ahora
  se valida cada valor (si es inválido se ignora) y solo se repinta si
  cambió.
- `data_manager.py`: el mismo RUT en distinto formato (`12.345.678-5` /
  `123456785`) creaba cuentas distintas; ahora la clave se normaliza.
- El aviso grande de notificaciones ahora sigue al banner si este cambia
  con el aviso abierto; se corrigió un comentario desactualizado.

### Solicitudes de RR.HH.: Vacaciones, Permiso y Licencia

Pedido del estudiante: implementar las 3 acciones rápidas (cada una en su
propia pantalla, con calendario, texto de motivo, menú desplegable, subir
archivo o tomar foto) y que cada una genere una notificación ("Sus
vacaciones fueron aprobadas") que, al tocarla, abra su sección y se quite.

- Decisiones que tomó la IA al no haber indicaciones en contra (el
  estudiante puede cambiarlas): un calendario propio (`CalendarPicker`) en
  vez del `MDDatePicker` de KivyMD, para respetar la paleta; un menú
  desplegable en línea en vez de `MDDropdownMenu`; y la **aprobación
  simulada** de RR.HH. (no hay backend), que dispara la notificación a los
  10 s.
- **Límite que la IA dejó explícito:** "se valida que sea una licencia" solo
  puede comprobarse como *documento utilizable* (formato, contenido real,
  peso, legibilidad); verificar que sea auténtica requeriría OCR o un
  backend. Está documentado en `README.md` y en `solicitudes.py`.
- Bugs encontrados al probar: un id de kv llamado `items` chocaba con el
  método `dict.items` de `ids`; el selector de archivos de Kivy trae texto
  blanco y era ilegible sobre fondo claro (se le dio fondo de la paleta); y
  los chips no centraban su texto porque `pos_hint` se ignora en un
  `BoxLayout`. También se ocultó un chevron del banner que quedaba visible
  con el banner vacío.
- Probado en modo headless: flujos completos de las 3 solicitudes, límites
  del calendario, validación de archivos buenos y malos, aprobación,
  notificación, apertura y eliminación, y persistencia tras cerrar y
  reabrir (las respuestas pendientes se retoman).

### Panel de administración: crear documentos para firmar

Pregunta del estudiante: ¿cómo se crean los documentos que los usuarios
firman? (idealmente con una cuenta específica o un panel de admin). La IA
respondió implementándolo: cuenta `admin@firmapp.cl` con rol `admin`
(`data_manager.get_role`), `AdminScreen` con formulario validado
(`solicitudes.validate_document`), cierre de sesión (`logout`) y
persistencia en `data/documentos.json`. Decisión de la IA, cambiable: los
documentos son globales (para todos los trabajadores), no por usuario.
Probado en headless: login admin, creación, título duplicado rechazado,
persistencia, ver el documento como trabajador, retirarlo.

### Listas de los menús desplegables

El estudiante entregó las listas reales (11 tipos de documento laboral y los
7 tipos de licencia médica chilena). La IA las usó como nombre corto +
descripción (`solicitudes.DOC_TYPES` / `LICENSE_TYPES`), y el menú
(`DropdownField`) ahora muestra la descripción bajo cada opción. Los nombres
de los tipos de documento se acortaron para que quepan en la tarjeta del
trabajador; la descripción conserva el texto completo.


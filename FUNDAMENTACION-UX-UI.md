# Fundamentación UX/UI — FirmApp (Interfaz de Recursos Humanos)

**Asignatura:** TINF1119 — Desarrollo Móvil (A+S)  
**Institución:** Instituto Tecnológico UC Temuco  
**Proyecto:** FirmApp (Maqueta Funcional en Kivy / KivyMD)  
**Integrantes:** `zikness`  

---

## 1. Metodología de Investigación de Usuarios (Subcriterio A1 — 5 pts)

Para el diseño centrado en el usuario de **FirmApp**, se aplicó un instrumento cuantitativo-cualitativo mediante un **formulario de diagnóstico en Google Forms** enfocado en el contexto del socio comunitario y la comunidad universitaria/laboral.

### Ficha Técnica de la Muestra
* **Total de participantes:** 11 respuestas completas.
* **Distribución por Rol Actual:**
  * **Otro:** 45,5 % (5 participantes)
  * **Estudiante (con ayudantía, pasantía o trabajo externo):** 27,3 % (3 participantes)
  * **Personal Administrativo / Profesional UCT:** 18,2 % (2 participantes)
  * **Docente / Académico(a) UCT:** 9,1 % (1 participante)
* **Tamaño de Organización de los Participantes:**
  * **Grande (más de 50 personas):** 36,4 % (4 participantes)
  * **No aplica / Independiente:** 27,3 % (3 participantes)
  * **Equipo pequeño (1 a 10 personas):** 18,2 % (2 participantes)
  * **Mediano (11 a 50 personas):** 18,2 % (2 participantes)

---

## 2. Resultados Principales con Evidencia (Subcriterio A2 — 10 pts)

A partir del análisis de las 11 respuestas recolectadas, se identificaron los siguientes hallazgos y evidencias clave:

1. **Alta Insatisfacción con el Proceso Actual:**
   * El **54,6 %** de los encuestados califica la rapidez y facilidad de su proceso actual como insatisfactorio (evaluado con notas **1 o 2** en escala de 1 a 5, con un **36,4 % evaluando con la nota mínima 1**).
2. **Fragmentación de Medios de Gestión:**
   * Un **50 % (5 de 10)** usa intranet o sistemas institucionales, pero coexiste con medios tradicionales: un **40 % (4 de 10)** gestiona en **papel impreso y firmando a mano** y otro **40 % (4 de 10)** mediante **archivos PDF por correo electrónico**.
3. **Puntos de Dolor y Frustraciones Principales:**
   * **36,4 % (4 encuestados):** Le frena tener que encender el computador sí o sí para realizar un trámite de RRHH.
   * **36,4 % (4 encuestados):** Se molesta por no recibir avisos ni notificaciones cuando hay documentos nuevos.
   * **27,3 % (3 encuestados):** Señala que las páginas web actuales no están optimizadas para la pantalla del teléfono celular.
   * **18,2 % (2 encuestados):** Manifiesta que los PDFs se pierden en el correo o que los documentos demoran mucho en ser firmados.
4. **Funcionalidades Más Demandadas para la App:**
   * **72,7 % (8 de 11 encuestados):** Exige **firmar contratos o liquidaciones de un toque desde el celular**.
   * **54,5 % (6 de 11 encuestados):** Requiere **pedir vacaciones o permisos administrativos en un par de clics**.
   * **45,5 % (5 de 11 encuestados):** Solicita **ver y descargar liquidaciones** y recibir **alertas/notificaciones push** al celular.
5. **Valoración de la Solución Móvil:**
   * El **54,5 % (6 de 11)** le asigna la máxima nota (**5/5**) a la utilidad de resolver estos trámites desde una app móvil en lugar de usar PC o ir presencialmente. Además, el **54,5 %** está dispuesto a probar la versión beta de la aplicación.

---

## 3. Matriz Hallazgo → Decisión de Diseño (UX/UI) (Subcriterio A3 — 10 pts)

La siguiente matriz conecta los resultados cuantitativos directos de la encuesta con las decisiones concretas implementadas en el código de **FirmApp** (Python + KivyMD):

| ID | Hallazgo Cuantitativo (Evidencia) | Decisión de Interfaz (UI/UX) en FirmApp | Justificación Técnica de Diseño |
| :--- | :--- | :--- | :--- |
| **H1** | **72,7 %** exige firmar documentos "de un toque" desde el celular. | **Botón "Firmar con 1 toque" en cada tarjeta pendiente (`PendingCard` → `SolidButton`, sobre `MDCard`):** cada documento de `PENDING` muestra su propio botón de firma; al tocarlo, la app navega directo a la pantalla **Firmar** (`SignScreen`) con ese documento ya cargado. | Elimina menús anidados y reduce la fricción, permitiendo iniciar la firma en 1 paso táctil desde el Dashboard. |
| **H2** | **36,4 %** rechaza encender la PC y **27,3 %** critica webs no adaptadas a móviles. | **Diseño Mobile-First Nativo (`420×880` px):** `Config.set('graphics', 'width'/'height', ...)` en `main.py` fija el tamaño de ventana a proporciones de teléfono móvil. | Garantiza una visualización limpia, elementos táctiles de tamaño adecuado e interfaz adaptada a pantallas verticales, sin depender de un computador. |
| **H3** | **36,4 %** sufre por no recibir avisos ni saber si hay documentos nuevos. | **Sección "Tareas Pendientes" con contador (`SectionLabel` + `PENDING`):** `RootScreen.on_kv_post()` puebla `pending_box` con una `PendingCard` por documento y muestra el total (`count`) en la parte superior del Dashboard. | Proporciona visibilidad clara del estado del sistema apenas se abre la app, sin obligar al usuario a buscar entre carpetas o correos. |
| **H4** | **54,5 %** pide gestionar permisos y vacaciones en "un par de clics". | **Accesos directos visibles en "Acciones Rápidas" (`QuickActionCard`):** las tarjetas "Pedir Vacaciones" y "Solicitar Permiso" se ubican en un lugar prioritario del Dashboard, antes que "Tareas Pendientes". | Responde a la demanda priorizando su visibilidad; **la pantalla de formulario para completar esas solicitudes queda fuera del alcance técnico de esta entrega** (ver nota más abajo) y es el siguiente paso de desarrollo. |
| **H5** | **40 %** aún depende del papel impreso o correos donde se pierden los PDFs. | **"Liquidaciones Recientes" con estado offline (`DocRow` + `RECENT`):** lista separada del Dashboard, con una etiqueta "Disponibles sin conexión" por cada documento ya guardado. | Centraliza la documentación laboral en un solo lugar dentro de la misma app, en vez de la bandeja de entrada del correo. |

> **Nota sobre H4:** en esta entrega, "Pedir Vacaciones" y "Solicitar Permiso"
> son accesos directos visuales sin una pantalla de formulario conectada
> todavía (no navegan a ningún lado al tocarlos). El alcance técnico de la
> evaluación (semana 8) cubre firma de documentos con `ScreenManager`, RUT y
> firma dibujada; la persistencia de solicitudes de permisos/vacaciones se
> evalúa en semanas posteriores. Se optó por dejar la demanda visible en el
> Dashboard (fiel al hallazgo) en lugar de ocultarla, dejando su
> implementación funcional como próximo paso.

---

## 4. Justificación de la Estructura de la App y Navegación (Subcriterio A4 — 3 pts)

La arquitectura de información de **FirmApp** responde a la necesidad de **rapidez e inmediatez** expresada por los usuarios (donde el 54,6 % calificó de difícil su sistema actual). La app se organiza con `kivy.uix.screenmanager.ScreenManager` en 9 pantallas, en un flujo Login/Registro → Inicio → Firmar → Éxito (más las pantallas de solicitud de Vacaciones, Permiso y Licencia y el panel de administración para crear documentos, a las que se llega desde las Acciones Rápidas o desde una notificación) (`InterfazRRHHApp.go_to_home_after_login()` / `go_to_register()` / `go_to_sign()` / `go_to_success()` / `go_home()`, con transición `FadeTransition`):

1. **Pantalla de Inicio de Sesión (`LoginScreen`) y de Registro (`RegisterScreen`):**
   * **Objetivo:** Identificar al trabajador con su RUT o correo (`LoginIdentifierInput`, con validación real del dígito verificador del RUT o formato de correo — ver `validators.py`) y una contraseña, autenticando contra las cuentas guardadas en `data/usuarios.json` (`DataManager.authenticate()` / `.register_user()` en `data_manager.py`), antes de mostrar cualquier documento. Quien no tiene cuenta puede crear una desde `RegisterScreen`, con el mismo campo RUT/correo, contraseña y confirmación de contraseña.
   * **Razón de UX:** Esta pantalla no proviene de un hallazgo puntual de la encuesta (la investigación se centró en el trámite de firma, no en el control de acceso), sino de un requisito funcional de la evaluación: controlar quién entra a sus propios documentos antes de nada. Se resolvió con **un solo campo** que acepta RUT o correo indistintamente — coherente con la prioridad de simplicidad que sí mostró la encuesta (72,7 % exige "de un toque", 36,4 % rechaza procesos largos): no se obliga al trabajador a recordar cuál de los dos usó para registrarse. El flujo Login ↔ Registro usa un enlace de texto ("¿No tienes cuenta? Regístrate" / "¿Ya tienes cuenta? Inicia sesión") en vez de una pantalla o menú aparte, para no agregar pasos a un trámite que la encuesta pide corto.
2. **Pantalla Principal / Dashboard (`HomeScreen`):**
   * **Objetivo:** Mostrar de forma inmediata el listado de `PENDING` (documentos por firmar) y `RECENT` (liquidaciones ya firmadas), además de los accesos directos de "Acciones Rápidas".
   * **Razón de UX:** Responde al **72,7 %** que busca firmar rápido y al **36,4 %** que necesita saber qué tiene pendiente apenas abre la aplicación.
3. **Pantalla de Firma (`SignScreen`):**
   * **Objetivo:** Confirmar la identidad e ingresar la firma del documento elegido en Inicio, con dos formas a elección: pestaña **"Ingresar RUT"** (formato automático `12.345.678-9`, `RutInput`) o pestaña **"Dibujar Firma"** (lienzo táctil, `SignaturePad`).
   * **Razón de UX:** Responde al **72,7 %** que exige firmar "de un toque" — reduce el trámite a un único paso adicional después de tocar "Firmar" en el Dashboard, sin campos ni pantallas de más.
4. **Pantalla de Confirmación (`SuccessScreen`):**
   * **Objetivo:** Mostrar la confirmación visual de que la firma se realizó, con botón para volver a Inicio.
   * **Razón de UX:** Da certeza al usuario de que el documento fue firmado correctamente, eliminando la incertidumbre del correo o el papel (hallazgo del 18,2 % que reporta PDFs perdidos en el correo).

> **Nota sobre `LoginScreen`/`RegisterScreen`:** autentican contra cuentas
> reales guardadas en `data/usuarios.json` (ver `data_manager.py`), no solo
> contra el formato del RUT/correo. El documento firmado también se
> persiste en `data/documentos.json` y sobrevive a cerrar y reabrir la
> app — ver la sección "Persistencia de datos (JSON)" de `README.md` y la
> actualización correspondiente en `USO_IA.md`.

---

## 5. Consideraciones de Diversidad y Accesibilidad (Subcriterio A5 — 2 pts)

Considerando que la muestra de usuarios incluye desde estudiantes con ayudantía hasta personal administrativo y docentes con variados niveles de familiaridad tecnológica y contextos de trabajo (desde independientes hasta organizaciones de más de 50 personas):

* **Claridad Tipográfica y Jerarquía Visual:** Se aplican las directrices de Material Design a través de KivyMD, utilizando contraste de color adecuado para lectura en dispositivos móviles en cualquier entorno laboral.
* **Blanqueo de Tecnology Gap (Brecha Digital):** Al diseñar botones amplios (`SolidButton`, sobre `MDCard`) y tarjetas interactivas (`PressCard`, con animación de pulsado/hover), se facilita el toque para personas no familiarizadas con interfaces complejas de escritorio o intranets institucionales tradicionales.
* **Mensajes Claros y Directos:** Se evita el lenguaje burocrático, utilizando nomenclaturas cotidianas como *"Firmar"*, *"Pendientes"* y *"Permisos"*.
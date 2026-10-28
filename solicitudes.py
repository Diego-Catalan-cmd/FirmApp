# -*- coding: utf-8 -*-
"""
solicitudes.py
Reglas de negocio de las 3 solicitudes de RR.HH. (Vacaciones, Permiso y
Licencia). Funciones puras, casi sin Kivy: aqui viven las validaciones y los
textos, para poder ubicarlas y explicarlas en la defensa sin abrir la
interfaz (igual que validators.py).

  - Vacaciones: un rango de fechas (dias corridos, desde hoy), limitado por
    el saldo de dias disponibles, mas un motivo.
  - Permiso: dia libre por fuerza mayor, de 1 a PERMIT_MAX_DAYS (3) dias.
  - Licencia: tipo de licencia + archivo (PDF o imagen) o foto, que se valida
    con validate_license_file().
"""
import os
import uuid
from datetime import date, datetime

VACATION_BALANCE = 12      # dias de vacaciones disponibles al inicio
PERMIT_MAX_DAYS = 3        # un permiso es de 1 a 3 dias (no son vacaciones)
REASON_MIN = 10            # largo minimo del motivo (caracteres)
REASON_MAX = 300

LICENSE_TYPES = [
    'Licencia médica (enfermedad común)',
    'Licencia por accidente laboral',
    'Licencia pre y postnatal',
    'Licencia por enfermedad grave de hijo(a)',
]
LICENSE_MIN_BYTES = 10 * 1024          # un documento real pesa mas de 10 KB
LICENSE_MAX_BYTES = 10 * 1024 * 1024   # tope de 10 MB
LICENSE_MIN_SIDE = 400                 # px: una foto legible de un documento
LICENSE_EXTS = ('.pdf', '.png', '.jpg', '.jpeg')
IMAGE_EXTS = ('.png', '.jpg', '.jpeg')

DOC_TYPES = ['Contrato', 'Liquidación', 'Anexo de contrato', 'Finiquito']
DOC_TITLE_MIN, DOC_TITLE_MAX = 5, 80
DOC_MAX_PAGES = 200

MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun',
         'jul', 'ago', 'sep', 'oct', 'nov', 'dic']
MESES_LARGO = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio',
               'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

# Textos y icono de cada tipo de solicitud (el icono es un nombre de icons.py).
KINDS = {
    'vacaciones': dict(label='Vacaciones', icon='vacation',
                       approved='Sus vacaciones fueron aprobadas'),
    'permiso': dict(label='Permiso', icon='permit',
                    approved='Su permiso fue aprobado'),
    'licencia': dict(label='Licencia', icon='camera',
                     approved='Su licencia fue validada y aprobada'),
}


# ------------------------------------------------------------------ fechas
def to_date(iso):
    return datetime.strptime(iso, '%Y-%m-%d').date()


def count_days(start, end):
    """Dias corridos del rango, ambos extremos incluidos."""
    return (end - start).days + 1


def fmt_day(d):
    return '%d %s' % (d.day, MESES[d.month - 1])


def fmt_range(start, end):
    """'12 – 16 nov', '30 oct – 2 nov' o '12 nov' si es un solo dia."""
    if start == end:
        return fmt_day(start)
    if start.month == end.month:
        return '%d – %s' % (start.day, fmt_day(end))
    return '%s – %s' % (fmt_day(start), fmt_day(end))


def plural_days(n):
    return '%d día%s' % (n, '' if n == 1 else 's')


# ------------------------------------------------------------ validaciones
def _check_reason(reason):
    reason = (reason or '').strip()
    if len(reason) < REASON_MIN:
        return 'Cuéntanos el motivo (mínimo %d caracteres).' % REASON_MIN
    return None


def validate_vacation(start, end, reason, available, today=None):
    """(ok, mensaje). Rango completo, desde hoy, dentro del saldo."""
    today = today or date.today()
    if not start or not end:
        return False, 'Elige el primer y el último día en el calendario.'
    if start < today:
        return False, 'No puedes pedir vacaciones en fechas pasadas.'
    if end < start:
        return False, 'La fecha de término es anterior a la de inicio.'
    if count_days(start, end) > available:
        return False, 'Solo tienes %s disponibles.' % plural_days(available)
    err = _check_reason(reason)
    return (False, err) if err else (True, '')


def validate_permit(start, end, reason, today=None):
    """(ok, mensaje). Un permiso es de 1 a PERMIT_MAX_DAYS dias."""
    today = today or date.today()
    if not start or not end:
        return False, 'Elige el día (o los días) en el calendario.'
    if start < today:
        return False, 'No puedes pedir un permiso en fechas pasadas.'
    if count_days(start, end) > PERMIT_MAX_DAYS:
        return False, 'Un permiso es de 1 a %d días.' % PERMIT_MAX_DAYS
    err = _check_reason(reason)
    return (False, err) if err else (True, '')


def _magic_matches(head, ext):
    if ext == '.pdf':
        return head.startswith(b'%PDF')
    if ext == '.png':
        return head.startswith(b'\x89PNG\r\n\x1a\n')
    return head.startswith(b'\xff\xd8\xff')          # .jpg / .jpeg


def validate_license_file(path, from_camera=False, image_size=None):
    """
    Valida que el archivo sirva como licencia. (ok, mensaje).

    OJO -- alcance real: sin un backend ni OCR, la app NO puede leer el
    contenido ni comprobar que el documento sea autentico (eso lo revisa
    RR.HH. / COMPIN). Lo que SI verifica es que sea un documento utilizable:
      1. existe y es un archivo,
      2. tiene formato permitido (PDF, PNG o JPG; solo imagen si viene de la
         camara),
      3. su contenido real coincide con la extension (no es un .exe o un
         .txt renombrado a .pdf),
      4. su peso es razonable (10 KB a 10 MB),
      5. si es imagen, tiene resolucion suficiente para leerse
         (image_size = (ancho, alto), lo mide quien llama con Kivy),
      6. si es PDF, esta completo (trae la marca final %%EOF).
    """
    if not path or not os.path.isfile(path):
        return False, 'No se encontró el archivo.'
    ext = os.path.splitext(path)[1].lower()
    allowed = IMAGE_EXTS if from_camera else LICENSE_EXTS
    if ext not in allowed:
        return False, ('Formato no permitido. Sube un PDF, PNG o JPG.'
                       if not from_camera else 'La foto debe ser PNG o JPG.')
    size = os.path.getsize(path)
    if size < LICENSE_MIN_BYTES:
        return False, 'El archivo es muy liviano para ser una licencia.'
    if size > LICENSE_MAX_BYTES:
        return False, 'El archivo supera los 10 MB.'
    try:
        with open(path, 'rb') as f:
            head = f.read(16)
            if ext == '.pdf':
                f.seek(max(0, size - 2048))
                tail = f.read()
    except OSError:
        return False, 'No se pudo leer el archivo.'
    if not _magic_matches(head, ext):
        return False, 'El contenido no corresponde a un %s válido.' % ext[1:].upper()
    if ext == '.pdf' and b'%%EOF' not in tail:
        return False, 'El PDF está incompleto o dañado.'
    if ext != '.pdf':
        if not image_size:
            return False, 'No se pudo abrir la imagen.'
        if min(image_size) < LICENSE_MIN_SIDE:
            return False, ('La imagen es muy pequeña para leerse. '
                           'Toma la foto más de cerca.')
    return True, 'Documento válido: formato, peso y legibilidad correctos.'


def fmt_deadline(d):
    """'20 Nov 2026': el mismo formato de los documentos de ejemplo."""
    return '%02d %s %d' % (d.day, MESES[d.month - 1].capitalize(), d.year)


def validate_document(doc_type, title, deadline, pages_text, existing_titles, today=None):
    """(ok, mensaje). Reglas del panel de administracion al crear un
    documento por firmar: tipo elegido, titulo unico de 5 a 80 caracteres,
    fecha limite desde hoy y entre 1 y 200 paginas. El titulo debe ser unico
    porque identifica al documento al firmarlo (complete_signature)."""
    today = today or date.today()
    title = (title or '').strip()
    if not doc_type:
        return False, 'Elige el tipo de documento.'
    if not (DOC_TITLE_MIN <= len(title) <= DOC_TITLE_MAX):
        return False, 'El título debe tener entre %d y %d caracteres.' % (DOC_TITLE_MIN, DOC_TITLE_MAX)
    if title.lower() in (t.lower() for t in existing_titles):
        return False, 'Ya existe un documento con ese título.'
    if not deadline:
        return False, 'Elige la fecha límite en el calendario.'
    if deadline < today:
        return False, 'La fecha límite no puede ser anterior a hoy.'
    if not (pages_text or '').strip().isdigit() or not (1 <= int(pages_text) <= DOC_MAX_PAGES):
        return False, 'Las páginas deben ser un número entre 1 y %d.' % DOC_MAX_PAGES
    return True, ''


# ----------------------------------------------------------------- registros
def new_request(kind, **fields):
    """Registro de una solicitud, listo para guardarse en JSON."""
    return dict(id=uuid.uuid4().hex[:8], kind=kind, status='pendiente',
                created=datetime.now().isoformat(timespec='seconds'), **fields)


def request_title(req):
    """Linea principal que se muestra en la lista de solicitudes."""
    if req['kind'] == 'licencia':
        return req.get('license_type', 'Licencia')
    start, end = to_date(req['start']), to_date(req['end'])
    return '%s · %s' % (fmt_range(start, end), plural_days(req['days']))


def request_detail(req):
    if req['kind'] == 'licencia':
        return req.get('filename', '')
    return req.get('reason', '')


def approval_message(req):
    """Texto de la notificacion cuando RR.HH. responde."""
    base = KINDS[req['kind']]['approved']
    if req['kind'] == 'licencia':
        return base
    start, end = to_date(req['start']), to_date(req['end'])
    return '%s (%s)' % (base, fmt_range(start, end))

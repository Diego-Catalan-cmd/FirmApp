# -*- coding: utf-8 -*-
"""
validators.py
Validacion del identificador de inicio de sesion: RUT chileno (con digito
verificador real, modulo 11 -- no solo el largo, a diferencia de RutInput
en widgets.py, que valida la firma de un documento ya elegido y solo
necesita un chequeo visual) o correo electronico (nombre@dominio.com).

Funciones puras, sin nada de Kivy: se pueden ubicar y probar solas durante
la defensa del codigo, y es el lugar logico donde "ponerle un error a
proposito" (criterio 4 de la rubrica, Modificacion en vivo) sin tocar la
interfaz.
"""
import re

# nombre@dominio.tld -- exige al menos un punto en el dominio y un TLD de
# 2+ letras, como pide la evaluacion ("con el formato, es decir
# nombre@gmail.com").
EMAIL_RE = re.compile(r'^[\w.+-]+@[\w-]+\.[A-Za-z]{2,}$')


def clean_rut(text):
    """Deja solo digitos y 'K' (el digito verificador puede ser K)."""
    return ''.join(c for c in text if c.isdigit() or c in 'kK')


def rut_check_digit(body):
    """
    Digito verificador de un RUT chileno, algoritmo modulo 11: cada digito
    del cuerpo (de derecha a izquierda) se multiplica por un factor que va
    de 2 a 7 y vuelve a empezar en 2; se suman los productos y el resultado
    es 11 menos el resto de esa suma dividida por 11 (0 si da 11, 'K' si
    da 10).
    """
    total = 0
    factor = 2
    for digit in reversed(body):
        total += int(digit) * factor
        factor = factor + 1 if factor < 7 else 2
    resto = 11 - (total % 11)
    if resto == 11:
        return '0'
    if resto == 10:
        return 'K'
    return str(resto)


def is_valid_rut(text):
    """True si 'text' (con o sin puntos/guion) es un RUT chileno valido de
    verdad -- compara el digito verificador calculado, no solo el largo."""
    clean = clean_rut(text)
    if len(clean) < 2:
        return False
    body, dv = clean[:-1], clean[-1].upper()
    if not body.isdigit() or not (7 <= len(body) <= 8):
        return False
    return rut_check_digit(body) == dv


def is_valid_email(text):
    """True si 'text' tiene forma de correo (nombre@dominio.com)."""
    return bool(EMAIL_RE.match(text.strip()))


def identify(text):
    """
    Clasifica 'text' como RUT o correo segun si tiene '@', y lo valida con
    la funcion que corresponda. Devuelve (tipo, valido):
        ('rut', True/False)    si no tiene '@'
        ('email', True/False)  si tiene '@'
        (None, False)          si esta vacio
    """
    text = text.strip()
    if not text:
        return (None, False)
    if '@' in text:
        return ('email', is_valid_email(text))
    return ('rut', is_valid_rut(text))

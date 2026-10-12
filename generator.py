"""Modelo y generación de HTML: sin llamadas externas ni JavaScript en Moodle."""
import copy
import html
import json
import re
from urllib.parse import urlsplit
from uuid import uuid4

TYPES = ['Texto', 'Texto destacado', 'Tarjeta con enlace', 'Materiales', 'Actividad', 'Encuentro sincrónico', 'Imagen']
PALETTES = {
    'Verde CITEP': ('#006434', '#eef5ef', '#ffffff', '#24362b'),
    'Oliva y arena': ('#59613b', '#eae5dc', '#ffffff', '#3e362e'),
    'Coral y fucsia': ('#d12e67', '#fff0e7', '#ffffff', '#55263b'),
    'Azul': ('#215f98', '#eef4fa', '#ffffff', '#25364a'),
}
FONTS = {'Sans serif': 'Arial, Helvetica, sans-serif', 'Serif': 'Georgia, Times, serif'}


def new_block(kind='Texto', **values):
    block = dict(id=uuid4().hex, type=kind, title=kind, text='', url='', button='Ingresar',
                 image='', alt='', items='', date='', time='', location='', new_tab=True)
    block.update(values)
    return block


def new_project(mode='Sección del curso'):
    page = mode == 'Página de Moodle'
    return dict(version=1, mode=mode, title='Título de la página' if page else 'Nuestra ruta de trabajo',
                subtitle='Introducción, materiales y actividades', intro='Te invitamos a recorrer esta propuesta y participar de las actividades.',
                primary='#006434', background='#eef5ef', card='#ffffff', text_color='#24362b',
                font='Sans serif', width=1000, layout='Una columna',
                blocks=[new_block('Texto' if page else 'Texto destacado', title='Para comenzar', text='Presentá aquí el tema y los objetivos de esta propuesta.'),
                        new_block('Materiales', title='Materiales para explorar', items='Lectura de referencia | https://example.org/material'),
                        new_block('Actividad', title='Manos a la obra', text='Compartí tus ideas en el espacio de intercambio.', items='Revisá los materiales.\nElaborá tu aporte.\nCompartilo con el grupo.', button='Ir a la actividad')])


def safe_url(value, image=False):
    value = value.strip()
    if not value:
        return ''
    if any(ord(c) < 33 for c in value) or '\\' in value:
        raise ValueError('El enlace contiene espacios o caracteres no válidos.')
    try:
        p = urlsplit(value)
        if p.scheme in ('https', 'http') and p.hostname and not p.username and not p.password:
            _ = p.port
            return value
        if not image and p.scheme == 'mailto' and p.path and '@' in p.path:
            return value
    except ValueError:
        pass
    raise ValueError('Usá un enlace completo que comience con https:// o http://' + ('.' if image else ', o mailto: para un correo.'))


def material_rows(value):
    rows = []
    for n, line in enumerate(value.splitlines(), 1):
        if not line.strip():
            continue
        label, sep, url = line.partition('|')
        if not sep or not label.strip() or not url.strip():
            raise ValueError(f'Materiales, línea {n}: escribí Nombre del material | https://…')
        try:
            rows.append((label.strip(), safe_url(url)))
        except ValueError as e:
            raise ValueError(f'Materiales, línea {n}: {e}') from e
    return rows


def validate(project):
    errors = []
    for i, b in enumerate(project['blocks'], 1):
        prefix = f'Bloque {i} ({b["title"] or b["type"]})'
        try:
            if b['type'] in ('Tarjeta con enlace', 'Actividad', 'Encuentro sincrónico'):
                safe_url(b['url'])
            if b['type'] in ('Tarjeta con enlace', 'Imagen'):
                safe_url(b['image'], image=True)
                if b['image'].strip() and not b['alt'].strip():
                    errors.append(f'{prefix}: agregá una descripción de la imagen.')
            if b['type'] == 'Materiales':
                material_rows(b['items'])
        except ValueError as e:
            errors.append(f'{prefix}: {e}')
    return errors


def esc(value):
    return html.escape(value, quote=True)


def paragraphs(value):
    return ''.join('<p style="margin:0 0 12px;">' + esc(p).replace('\n', '<br>') + '</p>'
                   for p in re.split(r'\n\s*\n', value.strip()) if p.strip())


def link(label, url, new_tab, style=''):
    target = ' target="_blank" rel="noopener noreferrer"' if new_tab else ''
    return f'<a href="{esc(safe_url(url))}"{target} style="{style}">{esc(label)}</a>'


def render_fragment(p):
    errors = validate(p)
    if errors:
        raise ValueError('\n'.join(errors))
    primary, bg, card, color = (p[k] for k in ('primary', 'background', 'card', 'text_color'))
    button_style = f'display:inline-block;background:{primary};color:{contrast_text(primary)};padding:10px 18px;border-radius:8px;text-decoration:none;font-weight:bold;max-width:100%;box-sizing:border-box;'
    output = [f'<div lang="es" style="box-sizing:border-box;max-width:{p["width"]}px;margin:0 auto;padding:24px;background:{bg};color:{color};font-family:{FONTS[p["font"]]};font-size:16px;line-height:1.6;overflow-wrap:anywhere;">']
    if p['subtitle']:
        output.append(f'<p style="margin:0 0 8px;color:{color};font-size:14px;">{esc(p["subtitle"])}</p>')
    title_size = 28 if p['mode'] == 'Sección del curso' else 32
    if p['title']:
        output.append(f'<h2 style="margin:0 0 16px;color:{primary};font-size:{title_size}px;line-height:1.2;">{esc(p["title"])}</h2>')
    output.append(paragraphs(p['intro']))
    columns = p['layout'] == 'Dos columnas adaptables'
    output.append('<div style="display:flex;flex-wrap:wrap;gap:16px;align-items:stretch;">' if columns else '<div>')
    for b in p['blocks']:
        style = ('flex:1 1 300px;min-width:0;' if columns else 'margin-bottom:16px;')
        style += f'box-sizing:border-box;padding:22px;border-radius:12px;background:{card};border:1px solid {primary};color:{color};'
        if b['type'] == 'Texto destacado':
            style += f'border-left:6px solid {primary};'
        content = []
        if b['title']:
            content.append(f'<h3 style="margin:0 0 12px;color:{primary};font-size:22px;line-height:1.3;">{esc(b["title"])}</h3>')
        if b['type'] in ('Tarjeta con enlace', 'Imagen') and b['image'].strip():
            content.append(f'<img src="{esc(safe_url(b["image"], image=True))}" alt="{esc(b["alt"])}" style="display:block;max-width:100%;width:100%;height:auto;border-radius:8px;margin-bottom:14px;">')
        content.append(paragraphs(b['text']))
        if b['type'] == 'Materiales':
            content.append('<ul style="margin:0;padding-left:24px;">')
            for label, url in material_rows(b['items']):
                content.append('<li style="margin-bottom:10px;">' + link(label, url, b['new_tab'], f'color:{primary};text-decoration:underline;font-weight:bold;') + '</li>')
            content.append('</ul>')
        if b['type'] == 'Actividad' and b['items'].strip():
            content.append('<ol style="margin:0 0 16px;padding-left:24px;">' + ''.join(f'<li style="margin-bottom:8px;">{esc(x.strip())}</li>' for x in b['items'].splitlines() if x.strip()) + '</ol>')
        if b['type'] == 'Encuentro sincrónico':
            for label, key in [('Fecha', 'date'), ('Horario', 'time'), ('Modalidad / lugar', 'location')]:
                if b[key]:
                    content.append(f'<p style="margin:0 0 8px;"><strong>{label}:</strong> {esc(b[key])}</p>')
        if b['type'] in ('Tarjeta con enlace', 'Actividad', 'Encuentro sincrónico') and b['url'].strip():
            content.append(link(b['button'].strip() or 'Ingresar', b['url'], b['new_tab'], button_style))
        output.append('<div style="' + style + '">' + '\n'.join(content) + '</div>')
    output.append('</div>\n</div>')
    return '\n'.join(output)


def contrast_text(hex_color):
    rgb = [int(hex_color[i:i+2], 16) / 255 for i in (1, 3, 5)]
    linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in rgb]
    luminance = sum(v * w for v, w in zip(linear, [.2126, .7152, .0722]))
    return '#000000' if (luminance + .05) / .05 > 1.05 / (luminance + .05) else '#ffffff'


def document(fragment, title):
    return '<!DOCTYPE html>\n<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>' + esc(title) + '</title></head><body style="margin:0;padding:16px;">' + fragment + '</body></html>'


def export_project(p):
    return json.dumps(p, ensure_ascii=False, indent=2)


def import_project(raw):
    try:
        data = json.loads(raw)
    except (ValueError, UnicodeDecodeError) as e:
        raise ValueError('El archivo no es un proyecto JSON válido.') from e
    if not isinstance(data, dict) or data.get('version') != 1:
        raise ValueError('Formato o versión de proyecto no compatible.')
    p = new_project()
    for key in ('mode', 'title', 'subtitle', 'intro', 'primary', 'background', 'card', 'text_color', 'font', 'layout'):
        if not isinstance(data.get(key), str) or len(data[key]) > 100000:
            raise ValueError(f'Campo inválido: {key}.')
        p[key] = data[key]
    if p['mode'] not in ('Sección del curso', 'Página de Moodle') or p['font'] not in FONTS or p['layout'] not in ('Una columna', 'Dos columnas adaptables'):
        raise ValueError('Modo, tipografía o distribución no compatible.')
    for key in ('primary', 'background', 'card', 'text_color'):
        if not re.fullmatch(r'#[0-9a-fA-F]{6}', p[key]):
            raise ValueError(f'Color inválido: {key}.')
    if type(data.get('width')) is not int or not 500 <= data['width'] <= 1400:
        raise ValueError('El ancho debe estar entre 500 y 1400.')
    p['width'] = data['width']
    if not isinstance(data.get('blocks'), list) or len(data['blocks']) > 50:
        raise ValueError('El proyecto admite hasta 50 bloques.')
    p['blocks'] = []
    for item in data['blocks']:
        if not isinstance(item, dict) or item.get('type') not in TYPES:
            raise ValueError('Tipo de bloque no compatible.')
        block = new_block(item['type'])
        for key in block:
            if key == 'id':
                continue
            value = item.get(key)
            if key == 'new_tab':
                if type(value) is not bool:
                    raise ValueError('La opción de apertura del enlace no es válida.')
            elif not isinstance(value, str) or len(value) > 100000:
                raise ValueError(f'Campo de bloque inválido: {key}.')
            block[key] = value
        p['blocks'].append(block)
    errors = validate(p)
    if errors:
        raise ValueError('\n'.join(errors))
    return p


def duplicate(block):
    result = copy.deepcopy(block)
    result['id'] = uuid4().hex
    return result

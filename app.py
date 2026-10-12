import streamlit as st
from generator import (TYPES, PALETTES, FONTS, new_project, new_block, duplicate,
                       render_fragment, document, export_project, import_project, validate)

st.set_page_config(page_title='Generador de bloques HTML · Moodle', page_icon='🧩', layout='wide')
st.title('🧩 Generador de bloques HTML')
st.caption('Una vuelta al Moodle · Combiná bloques y llevá el contenido a tu aula.')
if 'project' not in st.session_state:
    st.session_state.project = new_project()
    st.session_state.revision = 0


def load(p):
    st.session_state.project = p
    st.session_state.revision += 1


p = st.session_state.project
rev = st.session_state.revision

def field(label, obj, key, widget='text_input', **kwargs):
    widget_key = f'{rev}_{obj.get("id", "project")}_{key}'
    if widget_key not in st.session_state:
        st.session_state[widget_key] = obj[key]
    obj[key] = getattr(st, widget)(label, key=widget_key, **kwargs)
    return obj[key]


with st.sidebar:
    st.header('Tu proyecto')
    field('Destino', p, 'mode', 'selectbox', options=['Sección del curso', 'Página de Moodle'])
    st.caption('Podés cambiar de destino conservando tus bloques. Las plantillas iniciales se cargan con el botón de abajo.')
    if st.button('Cargar plantilla inicial', width="stretch"):
        load(new_project(p['mode']))
        st.rerun()
    st.caption('La plantilla reemplaza el contenido actual. Descargá tu proyecto antes si querés conservarlo.')
    st.divider()
    st.subheader('Identidad visual')
    palette = st.selectbox('Paleta sugerida', list(PALETTES), key='palette')
    if st.button('Aplicar paleta', width="stretch"):
        for key, value in zip(('primary', 'background', 'card', 'text_color'), PALETTES[palette]):
            p[key] = value
            st.session_state[f'{rev}_project_{key}'] = value
    field('Color principal', p, 'primary', 'color_picker')
    field('Fondo general', p, 'background', 'color_picker')
    field('Fondo de los bloques', p, 'card', 'color_picker')
    field('Color del texto', p, 'text_color', 'color_picker')
    field('Tipografía', p, 'font', 'selectbox', options=list(FONTS))
    field('Ancho máximo (px)', p, 'width', 'slider', min_value=500, max_value=1400, step=10)
    field('Distribución', p, 'layout', 'selectbox', options=['Una columna', 'Dos columnas adaptables'])
    st.divider()
    st.subheader('Retomar un proyecto')
    upload = st.file_uploader('Subí tu proyecto .json', type=['json'], key=f'upload_{rev}')
    if st.button('Abrir proyecto', disabled=upload is None, width="stretch"):
        if upload.size > 2_000_000:
            st.error('El archivo debe pesar menos de 2 MB.')
        else:
            try:
                load(import_project(upload.getvalue()))
                st.rerun()
            except ValueError as e:
                st.error(str(e))
    st.caption('El archivo JSON conserva textos, colores y bloques para seguir editando. La app no guarda los cambios al cerrar la sesión.')

edit, preview, output, help_tab = st.tabs(['1 · Editar', '2 · Vista previa', '3 · HTML y descargas', 'Cómo usarlo'])
with edit:
    st.subheader('Presentación')
    field('Título general', p, 'title')
    field('Texto breve sobre el título', p, 'subtitle')
    field('Introducción', p, 'intro', 'text_area', height=100)
    st.caption('Escribí texto normal. Una línea en blanco separa párrafos. Los símbolos <, > y & se conservan como texto.')
    st.subheader('Bloques de contenido')
    for index, b in enumerate(p['blocks']):
        with st.expander(f'{index + 1}. {b["type"]} · {b["title"] or "Sin título"}', expanded=len(p['blocks']) == 1):
            field('Título del bloque', b, 'title')
            field('Texto / descripción', b, 'text', 'text_area', height=100)
            kind = b['type']
            if kind in ('Tarjeta con enlace', 'Imagen'):
                field('URL de la imagen', b, 'image', placeholder='https://…')
                field('Descripción de la imagen (texto alternativo)', b, 'alt')
                st.caption('Usá una imagen ya alojada en Moodle o en una dirección accesible para tus estudiantes. No se suben imágenes desde esta app.')
            if kind == 'Materiales':
                field('Materiales: uno por línea', b, 'items', 'text_area', height=130,
                      help='Formato: Nombre del material | https://dirección-del-recurso')
            if kind == 'Actividad':
                field('Pasos: uno por línea (opcional)', b, 'items', 'text_area', height=110)
            if kind == 'Encuentro sincrónico':
                field('Fecha', b, 'date', placeholder='Viernes 30/10')
                field('Horario', b, 'time', placeholder='15 h · Argentina')
                field('Modalidad / lugar', b, 'location', placeholder='Por Zoom')
            if kind in ('Tarjeta con enlace', 'Actividad', 'Encuentro sincrónico'):
                field('Texto del botón', b, 'button')
                field('URL del botón (opcional)', b, 'url', placeholder='https://…')
                st.caption('Si dejás la URL vacía, no se muestra el botón.')
            if kind in ('Tarjeta con enlace', 'Materiales', 'Actividad', 'Encuentro sincrónico'):
                field('Abrir enlaces en otra pestaña', b, 'new_tab', 'checkbox')
            c1, c2, c3, c4 = st.columns(4)
            if c1.button('↑ Subir', key=f'up_{b["id"]}', disabled=index == 0):
                p['blocks'][index-1], p['blocks'][index] = b, p['blocks'][index-1]
                st.rerun()
            if c2.button('↓ Bajar', key=f'down_{b["id"]}', disabled=index == len(p['blocks'])-1):
                p['blocks'][index+1], p['blocks'][index] = b, p['blocks'][index+1]
                st.rerun()
            if c3.button('Duplicar', key=f'copy_{b["id"]}', disabled=len(p['blocks']) >= 50):
                p['blocks'].insert(index+1, duplicate(b))
                st.rerun()
            if c4.button('Quitar', key=f'delete_{b["id"]}'):
                p['blocks'].pop(index)
                st.rerun()
    add_type = st.selectbox('Tipo de bloque que querés agregar', TYPES)
    if st.button('＋ Agregar bloque', type='primary', disabled=len(p['blocks']) >= 50):
        p['blocks'].append(new_block(add_type))
        st.rerun()
    st.caption(f'{len(p["blocks"])} bloques · Hasta 50 por proyecto.')

errors = validate(p)
fragment = None
if not errors:
    fragment = render_fragment(p)

with preview:
    st.subheader('Vista previa del conjunto')
    viewport = st.radio('Ancho de la vista previa', ['Escritorio', 'Celular'], horizontal=True)
    if errors:
        st.error('Corregí los datos para generar la vista previa:\n\n' + '\n\n'.join(errors))
    else:
        preview_width = '390px' if viewport == 'Celular' else '100%'
        st.iframe(document('<div style="max-width:' + preview_width + ';margin:0 auto;">' + fragment + '</div>', p['title']), height=760, alt='Vista previa del contenido para Moodle')
    st.caption('La vista previa es orientativa. Revisá el resultado dentro de tu campus: el tema y el editor de Moodle pueden ajustar algunos estilos. La vista de celular simula el ancho del contenido.')
with output:
    st.subheader('HTML para pegar en Moodle')
    if errors:
        st.error('Hay datos por corregir:\n\n' + '\n\n'.join(errors))
    else:
        st.info('Copiá el código con el icono de la esquina superior derecha y pegalo en la opción de código fuente (HTML) del editor de Moodle.')
        st.code(fragment, language='html')
        st.download_button('Descargar fragmento HTML para Moodle', fragment, 'contenido-moodle.html', 'text/html')
        st.download_button('Descargar página HTML para abrir en el navegador', document(fragment, p['title']), 'vista-previa.html', 'text/html')
    st.divider()
    st.subheader('Guardar para seguir editando')
    st.download_button('Descargar proyecto editable (.json)', export_project(p), 'proyecto-bloques-moodle.json', 'application/json')
with help_tab:
    st.markdown('''
### De la app al aula
1. Elegí **Sección del curso** o **Página de Moodle**. Podés cargar su plantilla inicial.
2. Completá la presentación y los bloques. Agregá, duplicá, ordená o quitá los que necesites.
3. Elegí colores y distribución. Revisá la vista previa, también en el ancho de celular.
4. En **HTML y descargas**, copiá el fragmento HTML.
5. En Moodle, activá la edición y abrí el editor del destino. En su opción **código fuente / HTML**, pegá el código y guardá.

**Para una sección:** pegá el contenido en su descripción o en un recurso Texto y medios.

**Para una Página:** creá el recurso Página, completá su nombre y pegá el fragmento en **Contenido de la página**. La app prepara ese contenido; el nombre, la visibilidad y las restricciones se configuran en Moodle.

### Enlaces e imágenes
- Los materiales llevan una línea por recurso: `Nombre | https://…`.
- Los pasos de una actividad llevan una línea por paso.
- Usá las direcciones definitivas de los recursos y comprobá su acceso como estudiante. Evitá las direcciones temporales del editor de Moodle.
- La plantilla trae un enlace de ejemplo que debés reemplazar.
- El HTML usa estilos dentro de cada elemento, sin CSS externo ni JavaScript. Los textos se escriben como texto normal; esta versión no inserta HTML libre ni videos embebidos.

### Conservá tu trabajo
Descargá el **proyecto editable (.json)** antes de cerrar la app. Para continuarlo, subilo desde la barra lateral y pulsá **Abrir proyecto**. Descargar el HTML sirve para Moodle; el JSON sirve para volver a editar en esta app.
''')

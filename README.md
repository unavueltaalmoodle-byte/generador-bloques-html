# Generador de bloques HTML para Moodle · v1

Micro app en Python y Streamlit para combinar bloques y generar contenido para una sección del curso o un recurso Página de Moodle.

## Publicar con GitHub y Streamlit

1. Descomprimí este paquete.
2. En GitHub, creá un repositorio nuevo llamado `generador-bloques-html`. Mantené separado el repositorio del generador GIFT.
3. Entrá al repositorio y elegí **Add file → Upload files**. Subí los archivos de la carpeta descomprimida, de modo que `app.py`, `generator.py` y `requirements.txt` queden directamente en la raíz del repositorio. Podés incluir también este README y la carpeta `tests`.
4. Confirmá la carga con **Commit changes**.
5. En Streamlit Community Cloud, creá una app e indicá el repositorio `TU-USUARIO/generador-bloques-html`, la rama que tenga los archivos (normalmente `main`) y **Main file path: `app.py`**.
6. Publicá. No necesita claves, servicios pagos ni base de datos.

No subas el ZIP como un único archivo al repositorio: Streamlit necesita los archivos descomprimidos. No hace falta instalar Python en tu computadora para publicarla de esta manera.

## Primera prueba

1. Cambiá el título y los textos de la plantilla inicial.
2. En Materiales, reemplazá el enlace de ejemplo con un recurso real de tu campus. Formato: `Nombre del material | https://…`.
3. Agregá un encuentro sincrónico, completá sus datos y enlace.
4. Probá subir, bajar, duplicar y quitar bloques.
5. Elegí una paleta y revisá las vistas de escritorio y celular.
6. En **HTML y descargas**, copiá el fragmento con el icono de copiar del cuadro de código.
7. Pegalo en el código fuente HTML del editor de Moodle. Para una Página, usá el campo **Contenido de la página**. Guardá y revisá como estudiante.
8. Descargá el proyecto JSON; volvé a abrirlo desde la barra lateral para comprobar que conserva tu trabajo.

## Funciones

- Modos Sección del curso y Página de Moodle, con plantillas iniciales distintas.
- Texto, texto destacado, tarjeta con enlace, materiales, actividad, encuentro sincrónico e imagen.
- Agregar, ordenar, duplicar y quitar hasta 50 bloques.
- Una columna o dos columnas que se adaptan al espacio disponible.
- Cuatro paletas sugeridas y colores personalizados; tipografía serif o sans serif y ancho máximo.
- Vista previa con desplazamiento y simulación del ancho de celular.
- Copiar código; descargar fragmento para Moodle, página completa para abrir en el navegador y proyecto editable JSON.
- Validación de enlaces y proyectos importados; escapado de los textos y atributos HTML.

## Alcance de la primera versión

El HTML tiene estilos inline y no necesita archivos CSS externos ni JavaScript en Moodle. La vista previa es orientativa: el tema, los permisos y el editor del campus pueden modificar o filtrar algunos estilos. Esta primera versión usa texto normal; no admite HTML libre, videos embebidos, negritas parciales ni carga de imágenes. Las imágenes se agregan mediante una URL existente y un texto alternativo. Usá enlaces definitivos que sean accesibles para tus estudiantes y evitá enlaces temporales del editor.

La app genera contenido, no crea recursos ni configura restricciones en Moodle. Descargar HTML no conserva el proyecto editable: guardá también el JSON. Los cambios permanecen solo durante la sesión de la app; antes de cargar otra plantilla o cerrar, descargá el proyecto si querés conservarlo. Los enlaces de `example.org` son ejemplos y deben reemplazarse.

## Uso local opcional

Requiere Python 3.10 o posterior. Desde la carpeta del proyecto:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Pruebas para desarrollo:

```bash
python -m pip install pytest
python -m pytest -q
```

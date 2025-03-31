# Busqueda_Hospital_HUBU

Proyecto desarrollado en entorno hospitalario para automatizar la extracción de datos clínicos desde informes médicos en PDF, identificar ciertos criterios diagnósticos y cruzarlos con una base de datos en Excel. Por motivos de confidencialidad, no se incluyen ejemplos de ejecución ni archivos de salida, ya que el código fue utilizado con información sensible de pacientes.

Project developed in a hospital setting to automate the extraction of clinical data from medical reports in PDF format, identify specific diagnostic criteria, and cross-reference the results with an Excel database. Due to confidentiality reasons, no execution examples or output files are included, as the code was used with sensitive patient information.

---

# Extracción y análisis de informes médicos en formato PDF

Este proyecto permite extraer información estructurada desde informes médicos en formato PDF, aplicar filtros clínicos definidos y generar bases de datos en Excel para su posterior análisis o integración con otros sistemas.

Está diseñado para entornos hospitalarios que requieran:

- Procesamiento automático de grandes volúmenes de informes médicos.
- Detección de criterios diagnósticos específicos.
- Enlace de los resultados con bases de datos preexistentes (por ejemplo, bases de datos de biobanco).

---

## Funcionalidades principales

### 1. `extraer_informes_pdf(pdf_path)`
Extrae y analiza informes contenidos en un PDF. Para que un informe sea considerado válido, debe contener:

- Un número de historia clínica (NHC).
- Un número de muestra o biopsia.
- Una procedencia anatómica válida (por ejemplo: colon, sigma, recto, intestino grueso).
- Un diagnóstico.
- La presencia de la frase: "NO SE DETECTA pérdida".

Si se cumplen estos criterios, la información se almacena en un archivo Excel.

### 2. `guardar_en_excel(datos, output_path)`
Guarda los resultados extraídos en un archivo `.xlsx`.

### 3. `combinar_resultados(base_resultados, base_biobancbdd, output_final)`
Combina los resultados extraídos con una base de datos externa utilizando el campo común NHC. El resultado se guarda en un nuevo archivo Excel.

---

## Requisitos

Se detallan en el archivo [`requirements.txt`](./requirements.txt).*

*Para instalar todas las dependencias ejecute:
pip install -r requirements.txt


---

## Estructura esperada del proyecto
tu_proyecto/
  ├── archivo.pdf              # Informe PDF original
  ├── biobancbdd.xlsx          # Base de datos externa
  ├── resultados.xlsx          # Resultados extraídos del PDF
  ├── resultadosfinal.xlsx     # Resultados combinados
  ├── main.py                  # Código principal
  ├── README.md                # Descripción del proyecto
  └── requirements.txt         # Requisitos del entorno

---

## Estructura de entrada esperada (PDF)

Los informes médicos deben contener texto seleccionable (no imágenes o escaneos) y seguir una estructura coherente en la que se pueda identificar claramente información como el número de historia clínica, número de biopsia, procedencia anatómica, diagnóstico y resultado. El algoritmo está diseñado para manejar ligeras variaciones tipográficas o de formato, pero requiere que estos elementos estén presentes en el texto del informe.

---

## Ejecución

1. Colocar los archivos `archivo.pdf` y `biobancbdd.xlsx` en la carpeta de trabajo.
2. Ejecutar el archivo `main.py`.
3. Se generarán archivos Excel con los resultados obtenidos y su combinación con la base de datos externa.

---

## Notas

- El código ha sido probado con documentos PDF que contienen texto seleccionable. No funciona con documentos escaneados como imagen.
- La detección de patrones en los informes es flexible ante mayúsculas, acentos y pequeñas inconsistencias de formato.
- Por motivos de confidencialidad, este repositorio no incluye archivos de entrada, salida ni ejemplos de ejecución.

---

## Autor

Desarrollado por Diego Vallina Álvarez, estudiante de cuarto curso del Grado en Ingeniería de la Salud, durante su periodo de prácticas en el Hospital Universitario de Burgos (Área de Anatomía Patológica), a fecha de 31/03/2025.

Contacto: diego25codema@gmail.com


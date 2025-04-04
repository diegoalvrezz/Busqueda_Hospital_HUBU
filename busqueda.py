# -*- coding: utf-8 -*-
"""Busqueda.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1J8cbJcCivc7mZ3ukVlZn0KQpsvKeD4_y
"""

import re
import fitz  # PyMuPDF
import pandas as pd
import unidecode

########################
# Funciones auxiliares #
########################

def remove_accents(text: str) -> str:
    """Elimina acentos/tildes, para facilitar búsquedas insensibles a acentos."""
    return unidecode.unidecode(text)


def contiene_frase(base_text: str, frase: str) -> bool:
    """Verifica si `frase` (sin acentos y case-insensitive) está en `base_text`."""
    base_limpio = remove_accents(base_text.lower())
    frase_limpio = remove_accents(frase.lower())
    return frase_limpio in base_limpio


def extrae_patron(text: str, patron: str) -> str:
    """Devuelve la primera coincidencia (grupo 1) de `patron` en `text`, o None si no hay match."""
    match = re.search(patron, text, flags=re.IGNORECASE)
    if match and match.group(1).strip():
        return match.group(1).strip()
    return None

######################################
# Función principal de parseo INFORME #
######################################

def parse_informe(texto_informe: str) -> dict:
    """Parsea un bloque de texto que corresponde a un informe (un paciente)
    y devuelve un diccionario con los valores encontrados, o None si no cumple."""

    texto_informe = " ".join(texto_informe.split("\n"))  # Une líneas separadas

    # Extraer los datos con regex flexibles
    patron_nhc = r"(?i)n\s*h\s*c\s*[:\-]?\s*(\d{6})"
    patron_biopsia = r"(?i)nº\s*de\s*muestra\s*/?\s*biopsia\s*[:\-]?\s*(.+)"
    patron_procedencia = r"(?i)-\s*procedencia\s*anat[óo]mica\s*[:\-]?\s*([^\n]+)"
    patron_diagnostico = r"(?i)diagn[óo]stico\s*[:\-]?\s*([^\n]+)"

    nhc = extrae_patron(texto_informe, patron_nhc)
    biopsia = extrae_patron(texto_informe, patron_biopsia)
    procedencia_raw = extrae_patron(texto_informe, patron_procedencia)
    diagnostico = extrae_patron(texto_informe, patron_diagnostico)
    resultado_hallado = contiene_frase(texto_informe, "NO SE DETECTA pérdida")

    # Validar que procedencia contiene exclusivamente una de las palabras clave
    procedencia_valida = None
    if procedencia_raw:
        p_limpio = remove_accents(procedencia_raw.lower())
        palabras_validas = ["colon", "sigma", "recto", "intestino grueso"]
        if any(p_limpio.startswith(palabra) for palabra in palabras_validas):
            procedencia_valida = procedencia_raw.strip()
        else:
            return None  # Si no cumple, se descarta el informe

    # 🔍 DEBUG: Mostrar qué datos se están encontrando
    print("\n--- DEBUG: Información extraída ---")
    print(f"NHC detectado: {nhc}")
    print(f"Biopsia detectada: {biopsia}")
    print(f"Procedencia detectada: {procedencia_valida}")
    print(f"Diagnóstico detectado: {diagnostico}")
    print(f"Resultado detectado: {'Sí' if resultado_hallado else 'No'}")
    print("-----------------------------------\n")

    # Validación final: si falta algún dato, se descarta el informe
    if nhc and biopsia and procedencia_valida and diagnostico and resultado_hallado:
        return {
            "NHC": nhc,
            "Muestra/Biopsia": biopsia.strip(),
            "Procedencia": procedencia_valida,
            "Diagnostico": diagnostico.strip(),
            "Resultado": "NO SE DETECTA pérdida"
        }
    else:
        return None


############################################
# Función para procesar el PDF completo    #
############################################

def extraer_informes_pdf(pdf_path: str):
    """Lee todo el PDF y separa los informes en base a la aparición de 'Nº de muestra/biopsia'."""

    doc = fitz.open(pdf_path)
    lineas = [(pagenum + 1, t) for pagenum in range(len(doc)) for t in doc[pagenum].get_text("text").split("\n")]
    resultados = []

    i = 0
    while i < len(lineas):
        pageno, text_line = lineas[i]

        # 🔍 Buscar "Nº de muestra/biopsia:" en lugar de NHC
        if re.search(r"(?i)nº\s*de\s*muestra\s*/?\s*biopsia", text_line):
            bloque_inicio = i
            j = i + 1
            while j < len(lineas) and not re.search(r"(?i)nº\s*de\s*muestra\s*/?\s*biopsia", lineas[j][1]):
                j += 1
            chunk_text = "\n".join([l[1] for l in lineas[bloque_inicio:j]])
            informe_data = parse_informe(chunk_text)
            if informe_data:
                informe_data["Pagina"] = pageno
                resultados.append(informe_data)
            i = j
        else:
            i += 1
    return resultados

############################################
# Función para guardar resultados en Excel #
############################################

def guardar_en_excel(datos, output_path: str):
    df = pd.DataFrame(datos)
    df.to_excel(output_path, index=False)
    print(f"Resultados guardados en {output_path}")

############################################
# Función para combinar datos de Excel     #
############################################

def combinar_resultados(base_resultados: str, base_biobancbdd: str, output_final: str):
    """Combina los datos de resultados.xlsx con biobancbdd.xlsx mediante un JOIN en 'NHC' usando índices de columna."""

    # Cargar los archivos
    df_resultados = pd.read_excel(base_resultados)
    df_biobanc = pd.read_excel(base_biobancbdd)

    # 🔍 DEBUG: Mostrar nombres de columnas en biobancbdd.xlsx
    print("\n📌 Columnas en 'biobancbdd.xlsx':")
    print(df_biobanc.columns.tolist())

    # Seleccionar columnas usando índices
    try:
        df_biobanc = df_biobanc.iloc[:, [0, 1, 2, 3, 4, 5, 6, 7, 8]]  # Ajusta según el orden real en el archivo
        df_biobanc.columns = ["HC", "Fecha de obtención", "Caja", "Posición", "NHC",
                              "Codificador Morfológico 1", "Codificador Topográfico 1",
                              "Consentimiento", "Órgano"]
    except IndexError:
        print("❌ ERROR: El archivo 'biobancbdd.xlsx' no tiene suficientes columnas.")
        return

    # Realizar la combinación por NHC
    df_final = pd.merge(df_resultados, df_biobanc, on="NHC", how="left")

    # Guardar el nuevo Excel
    df_final.to_excel(output_final, index=False)
    print(f"✅ Archivo combinado guardado en {output_final}")


###########################################
# Ejemplo de uso                          #
###########################################
if __name__ == "__main__":
    pdf_path = "archivo.pdf"  # Cambiar por la ruta real
    output_excel = "resultados.xlsx"
    output_final_excel = "resultadosfinal.xlsx"
    base_biobancbdd = "biobancbdd.xlsx"  # Archivo externo

    # Extraer informes desde el PDF
    resultados = extraer_informes_pdf(pdf_path)
    if resultados:
        guardar_en_excel(resultados, output_excel)
        # Combinar con la base de datos externa
        combinar_resultados(output_excel, base_biobancbdd, output_final_excel)
    else:
        print("No se encontraron informes que cumplan todos los criterios.")

import pandas as pd

def merge_and_save_results(resultados_path, biobancbdd_path, output_path):
    # Cargar las bases de datos
    df_resultados = pd.read_excel(resultados_path)
    df_biobancbdd = pd.read_excel(biobancbdd_path)

    # Seleccionar las columnas deseadas de biobancbdd
    columns_to_keep = ["HC", "Fecha de obtención", "Caja", "Posición", "NHC",
                       "Codificador Morfológico 1", "Codificador Topográfico 1",
                       "Consentimiento", "Órgano"]
    df_biobancbdd = df_biobancbdd[columns_to_keep]

    # Realizar la unión de ambas bases de datos por el campo NHC
    df_merged = pd.merge(df_resultados, df_biobancbdd, on="NHC", how="left")

    # Guardar el resultado en un nuevo archivo Excel
    df_merged.to_excel(output_path, index=False)

    print(f"Archivo guardado exitosamente en {output_path}")

# Ejemplo de uso
merge_and_save_results("resultados.xlsx", "biobancbdd.xlsx", "RESULTADOS_FINALES.xlsx")

"""--- DEBUG: Información extraída ---
NHC detectado: 124168
Biopsia detectada: 22B-14462             -Procedencia anatómica: intestino grueso.   -Diagnóstico: adenoc
"""
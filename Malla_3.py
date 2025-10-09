import streamlit as st
import pandas as pd
from datetime import datetime
import re
from typing import Dict

# Definir los criterios predefinidos
tipo_documento = ["RC", "TI", "CC", "SC", "PT", "PE", "PA", "MS", "CN", "CE", "CD", "AS"]
regimen_validos = ["SUBSIDIADO", "CONTRIBUTIVO", "S", "C", "(S) SUBSIDIADO", "(C) CONTRIBUTIVO"]
rural_urbana_validos = ["URBANA", "RURAL", "R", "U", "URBANO", "urbano", "rural", "Rural", "Urbano", "Urbana"]
cobertura_validos = ["PBS", "pbs", "Pbs", "No pbs", "NO PBS", "No PBS", "No Pbs"]
tipo_entrega_validos = ["PENDIENTE", "TOTAL", "PARCIAL", "Pendiente", "Total", "Parcial", "pendiente", "total", "parcial"]
tipo_negociacion_validos = ["CAPITA", "EVENTO", "Capita", "Evento", "capita", "evento", "EVENTO PBS", "EVENTO NO PBS"]
nit_proveedor_validos = [
    "890985122", "900331412", "900716566", "900057926", "802000608", "900580962", "800149695", "828002423",
    "900994906", "892300678", "901048992", "900979320", "901433283", "860029216", "816001182", "900285194",
    "901200716", "900249425", "800149384", "900677118", "891408586", "900236850", "900095504", "900491883",
    "901776252", "830010337", "900382525", "900716452", "804008792", "830107855", "900098550", "901671387"
]

def cargar_archivo():
    archivo = st.file_uploader("Cargar archivo Excel", type=["xlsx", "xls"])
    return archivo

def validar_dataframe(df):
    errores_por_fila = []  # Lista para almacenar los errores por fila
    filas_con_errores = 0  # Contador de filas con errores       
    columnas_requeridas = [
        "TIPO DE IDENTIFICACIÓN", "NUMERO DE IDENTIFICACIÓN", "NOMBRE DEL USUARIO", 
        "RÉGIMEN", "DIRECCIÓN", "RURAL/URBANA", "NÚMERO DE CONTACTO", 
        "NÚMERO DE PRESCRIPCIÓN", "NIT IPS PRESCRIPTORA", "RAZÓN SOCIAL IPS", 
        "FECHA DE PRESCRIPCIÓN", "DX CIE-10 (1)", "DX CIE-10 (2)", "DX CIE-10 (3)", 
        "NÚMERO DE AUTORIZACIÓN", "NIT PROVEEDOR DISPENSA MEDICAMENTO", "RAZÓN SOCIAL PROVEEDOR", 
        "CÓDIGO NEGOCIADO", "CÓDIGO CUM", "NOMBRE PRODUCTO", "PRINCIPIO ACTIVO", 
        "CONCENTRACIÓN", "FORMA FARMACÉUTICA", "COBERTURA", "CÓDIGO DANE", 
        "DEPARTAMENTO", "MUNICIPIO", "FECHA DE SOLICITUD", "CANTIDAD SOLICITADA", 
        "FECHA DE ENTREGA", "CANTIDAD ENTREGADA", "TIPO DE ENTREGA", "NÚMERO DE PENDIENTE", 
        "FECHA DE ENTREGA PENDIENTES", "CANTIDAD ENTREGADA PENDIENTES", "VALOR UNITARIO", 
        "IVA", "VALOR TOTAL CON IVA", "ESTADO", "NÚMERO DE FACTURA", 
        "FECHA DE FACTURACIÓN", "FECHA RADICACIÓN FACTURACIÓN", "Cuota Moderadora", 
        "TIPO NEGOCIACION"
    ]
    
    # Recorremos las filas para validaciones
    for i, row in df.iterrows():
        fila_errores = []  # Lista para errores específicos de la fila
       
    # Normalización de nombres de columnas
    df.columns = df.columns.str.strip()  # Eliminar espacios extra
    df.columns = df.columns.str.upper()  # Convertir a mayúsculas

    # Verificar si falta alguna columna y mostrar alerta
    missing_columns = [col for col in columnas_requeridas if col not in df.columns]
    if missing_columns:
        st.warning(f"Faltan las siguientes columnas: {', '.join(missing_columns)}")
    
    # Lista de columnas de fecha que deseas validar
    fecha_columnas = ["FECHA DE PRESCRIPCIÓN", "FECHA DE SOLICITUD", "FECHA DE ENTREGA", "FECHA DE ENTREGA PENDIENTES"]
          
    # Recorremos cada fila del DataFrame
    for i, row in df.iterrows():
        fila_errores = []  # Lista para errores específicos de la fila
        fechas_convertidas = {}  # Guardar fechas válidas convertidas a datetime
        
        # Validación de fechas
        for columna in fecha_columnas:
            valor = row.get(columna, '')  
            
            # Intentar convertir a datetime sin importar el formato (acepta fecha con hora también)
            try:
                if pd.isna(valor) or str(valor).strip() == '':
                    continue  # Si está vacío, lo ignoramos (puedes marcarlo como error si lo necesitas)

                fecha_dt = pd.to_datetime(valor, dayfirst=True, errors='raise')
                fechas_convertidas[columna] = fecha_dt
            except Exception:
                fila_errores.append(f"ERROR FORMATO_{columna}")
                                    

        if pd.notna(row.get("NUMERO DE IDENTIFICACIÓN", None)):
            pass  # Aquí va tu lógica de validación
        else:
            fila_errores.append(f"Fila {i+1}: Falta 'NUMERO DE IDENTIFICACIÓN'")
        # Agregar más validaciones según tu lógica
        
        if pd.notna(row.get("TIPO DE IDENTIFICACIÓN", None)):
            if row["TIPO DE IDENTIFICACIÓN"].upper() not in tipo_documento:
                fila_errores.append("ERROR TIPO DE IDENTIFICACIÓN")
                
        # 6. Validar si existen datos en columnas clave y que no estén vacías
        if pd.notna(row.get("TIPO DE IDENTIFICACIÓN", None)) or pd.notna(row.get("NUMERO DE IDENTIFICACIÓN", None)):
            required_columns = [
            "NOMBRE DEL USUARIO", "RÉGIMEN", "RURAL/URBANA", "NÚMERO DE PRESCRIPCIÓN", "FECHA DE PRESCRIPCIÓN", "DX CIE-10 (1)", "NIT PROVEEDOR DISPENSA MEDICAMENTO", 
            "RAZÓN SOCIAL PROVEEDOR", "CÓDIGO NEGOCIADO", "CÓDIGO CUM", "NOMBRE PRODUCTO", "COBERTURA", 
            "CÓDIGO DANE", "FECHA DE SOLICITUD", "CANTIDAD SOLICITADA", "TIPO DE ENTREGA", "TIPO NEGOCIACION"
                ]
            for col in required_columns:
                if pd.isna(row.get(col, None)):
                    fila_errores.append(f"ERROR_{col}")

        # 7. Validación de "RÉGIMEN"
        if pd.notna(row.get("RÉGIMEN", None)):
            if row["RÉGIMEN"].upper() not in regimen_validos:
                fila_errores.append("ERROR RÉGIMEN")

        # 8. Validación de "RURAL/URBANA"
        if pd.notna(row.get("RURAL/URBANA", None)):
            if row["RURAL/URBANA"].upper() not in rural_urbana_validos:
                fila_errores.append("ERROR RURAL/URBANA")

        # 9. Validación de "COBERTURA"
        if pd.notna(row.get("COBERTURA", None)):
            if row["COBERTURA"].upper() not in cobertura_validos:
                fila_errores.append("ERROR COBERTURA")

        # 10. Validación de "NÚMERO DE PRESCRIPCIÓN" dependiendo de "COBERTURA"
        if pd.notna(row.get("COBERTURA", None)):
            if row["COBERTURA"].upper() in ["NO PBS", "NO PBS", "No PBS", "No Pbs"]:
                if not (pd.notna(row.get("NÚMERO DE PRESCRIPCIÓN", None)) and 
                        len(str(row["NÚMERO DE PRESCRIPCIÓN"])) in [20, 21]):
                    fila_errores.append("ERROR NÚMERO DE PRESCRIPCIÓN")

        # 11. Validación de "FECHA DE PRESCRIPCIÓN"
        if pd.notna(row.get("FECHA DE PRESCRIPCIÓN", None)):
            try:
                fecha_prescripcion = pd.to_datetime(row["FECHA DE PRESCRIPCIÓN"], errors='raise')
                if fecha_prescripcion.year < 2024:
                    fila_errores.append("ERROR FECHA DE PRESCRIPCIÓN")
            except Exception as e:
                fila_errores.append("ERROR FECHA DE PRESCRIPCIÓN")

        # 12. Validación de "DX CIE-10 (1)"
        if pd.notna(row.get("DX CIE-10 (1)", None)):
            cie10_pattern = r"^[A-Z]\d{2}[0-9X]$"
            dx = str(row["DX CIE-10 (1)"]).upper()  # ← Aquí conviertes a mayúscula
            if not re.match(cie10_pattern, dx):
                fila_errores.append("ERROR DX CIE-10 (1)")

        # 13. Validación de "NIT PROVEEDOR DISPENSA MEDICAMENTO"
        if pd.notna(row.get("NIT PROVEEDOR DISPENSA MEDICAMENTO", None)):
            nit_proveedor = str(row["NIT PROVEEDOR DISPENSA MEDICAMENTO"]).split('-')[0]  # Omitir "-XX"
            if nit_proveedor not in nit_proveedor_validos:
                fila_errores.append("ERROR NIT PROVEEDOR DISPENSA MEDICAMENTO")

        # 14. Validación de "CÓDIGO DANE"
        if pd.notna(row.get("CÓDIGO DANE", None)) and len(str(row["CÓDIGO DANE"])) != 5:
            fila_errores.append("ERROR DANE")

        # 17. Validación de "CANTIDAD SOLICITADA"
        if pd.notna(row.get("CANTIDAD SOLICITADA", None)):
            if row["CANTIDAD SOLICITADA"] < 1:
                fila_errores.append("ERROR CANTIDAD SOLICITADA")

        # 18. Validación de "CANTIDAD ENTREGADA"
        if pd.notna(row.get("FECHA DE ENTREGA", None)) and pd.isna(row.get("CANTIDAD ENTREGADA", None)):
            fila_errores.append("ERROR CANTIDAD ENTREGADA")

        # 20. Validación de "NÚMERO DE PENDIENTE"
        if pd.notna(row.get("FECHA DE ENTREGA PENDIENTES", None)) and pd.isna(row.get("NÚMERO DE PENDIENTE", None)):
            fila_errores.append("ERROR NÚMERO DE PENDIENTE")

        # 21. Validación de "CANTIDAD ENTREGADA PENDIENTES"
        if pd.notna(row.get("FECHA DE ENTREGA PENDIENTES", None)) and pd.isna(row.get("CANTIDAD ENTREGADA PENDIENTES", None)):
            fila_errores.append("ERROR CANTIDAD ENTREGADA PENDIENTES")

        # 22. Validación de "TIPO DE ENTREGA"
        if pd.notna(row.get("TIPO DE ENTREGA", None)) and row["TIPO DE ENTREGA"].upper() not in tipo_entrega_validos:
            fila_errores.append("ERROR TIPO ENTREGA")

        # 23. Validación de "Tipo Negociacion"
        if pd.notna(row.get("TIPO NEGOCIACION", None)) and row["TIPO NEGOCIACION"].upper() not in tipo_negociacion_validos:
            fila_errores.append("ERROR TIPO NEGOCIACION")
            
        # 24. Validacion "Cronologia"
        # Validación cronológica completa
        try:
            fecha_solicitud = pd.to_datetime(row["FECHA DE SOLICITUD"], errors='raise') if pd.notna(row.get("FECHA DE SOLICITUD", None)) else None
            fecha_prescripcion = pd.to_datetime(row["FECHA DE PRESCRIPCIÓN"], errors='raise') if pd.notna(row.get("FECHA DE PRESCRIPCIÓN", None)) else None
            fecha_entrega = pd.to_datetime(row["FECHA DE ENTREGA"], errors='raise') if pd.notna(row.get("FECHA DE ENTREGA", None)) else None
            fecha_entrega_pendiente = pd.to_datetime(row["FECHA ENTREGA PENDIENTE"], errors='raise') if pd.notna(row.get("FECHA ENTREGA PENDIENTE", None)) else None

            error_cronologia = False

        # 24.1. Fecha entrega pendiente > Fecha solicitud
            if fecha_entrega_pendiente and fecha_solicitud and fecha_entrega_pendiente <= fecha_solicitud:
                error_cronologia = True

        # 24.2. Fecha entrega >= Fecha solicitud
            if fecha_entrega and fecha_solicitud and fecha_entrega < fecha_solicitud:
                error_cronologia = True

        # 24.3. Fecha solicitud >= Fecha prescripción
            if fecha_solicitud and fecha_prescripcion and fecha_solicitud < fecha_prescripcion:
                error_cronologia = True

            if error_cronologia:
                fila_errores.append("ERROR_CRONOLOGIA")

        except Exception as e:
            fila_errores.append("ERROR_CRONOLOGIA")
        
        # Si hay errores en la fila
        if fila_errores:
            filas_con_errores += 1
            errores_por_fila.append(" | ".join(fila_errores))  # Errores separados por '|'
        else:
            errores_por_fila.append("")  # No hay errores en esta fila
    
    return errores_por_fila, filas_con_errores

# Ejemplo de DataFrame (puedes eliminar esta parte si ya tienes tu df cargado)
data = {
    "FECHA DE PRESCRIPCIÓN": ["15/03/2025", "2025-03-20", "13/45/2025"],  # La segunda y tercera son incorrectas
    "FECHA DE SOLICITUD": ["25/02/2025", "2025-03-22", "not a date"],  # Última no es una fecha válida
    "FECHA DE ENTREGA": ["10/03/2025", "15-03-2025", "11/03/2025"],  # La segunda es incorrecta
    "FECHA DE ENTREGA PENDIENTES": ["10/03/2025", "invalid date", "17/03/2025"]
}


def main():
    st.title("Validación Archivo de Dispensación")

    archivo = cargar_archivo()
    
    if archivo and "validado" not in st.session_state:
        # Cargar archivo
        df = pd.read_excel(archivo, header=1)  # Cargar el archivo Excel
        
        # Verificar y normalizar las columnas
        df.columns = df.columns.str.strip()  # Eliminar espacios en blanco extra
        df.columns = df.columns.str.upper()  # Convertir a mayúsculas
        
        # Validar el archivo y mostrar errores
        errores_por_fila, filas_con_errores = validar_dataframe(df)  
        
        # Guardar el estado de validación en session_state
        st.session_state.validado = True
        st.session_state.df = df
        st.session_state.errores_por_fila = errores_por_fila  
        
        # Mostrar el encabezado
        st.header(f"Archivo cargado: {archivo.name}")
        st.write(f"Fecha de validación: {datetime.now().strftime('%Y-%m-%d')}")
        
        # Mostrar el resumen de los errores
        st.write(f"Total de filas con incidencias: {filas_con_errores}")
        st.write(f"Total de filas sin incidencias: {len(df) - filas_con_errores}")

        # Crear una columna 'ERRORS' con los errores por fila
        df['ERRORS'] = errores_por_fila
        
        # Generar archivo Excel con los errores
        with st.expander("Descargar archivo con errores"):
            # Guardar el DataFrame con los errores en un archivo Excel
            output = "archivo_validado.xlsx"
            df.to_excel(output, index=False)
            
            # Descargar el archivo Excel
            with open(output, "rb") as file:
                st.download_button(
                    label="Descargar archivo con errores",
                    data=file,
                    file_name=output,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

if __name__ == "__main__":
    main()

# Crear el panel izquierdo
st.sidebar.title("Información Importante")

# Mostrar el texto informativo
st.sidebar.markdown("""
Recuerde tener en cuenta estos archivos para la presentación de la información, 
si presenta errores en la validación consulte la estructura e instructivo.
""")

# Función para descargar archivos
def download_file(file_path, file_name):
    with open(file_path, "rb") as f:
        st.sidebar.download_button(
            label=f"Descargar {file_name}",
            data=f,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# Botones para cada archivo
if st.sidebar.button("ESTRUCTURA DISPENSACION"):
    download_file:r"C:\Users\josabogal\Desktop\Proyecto\Malla\Estructura.xlsx"

if st.sidebar.button("INSTRUCTIVO"):
    download_file("path_to_your_file/instructivo.xlsx", "INSTRUCTIVO.xlsx")

if st.sidebar.button("HOMOLOGACION TIPO ID"):
    download_file("path_to_your_file/homologacion_tipo_id.xlsx", "HOMOLOGACION TIPO ID.xlsx")

if st.sidebar.button("INST. CARGUE INFORMACION"):
    download_file("path_to_your_file/inst_cargue_informacion.xlsx", "INST. CARGUE INFORMACION.xlsx")


if cargar_archivo is not None:
    df = pd.read_excel(cargar_archivo)  # Ahora sí pasas el archivo, no la función
    st.write("Columnas encontradas:", df.columns.tolist())
    validar_dataframe(df)
else:
    st.warning("Por favor carga un archivo")
import streamlit as st
import os
import json
import tempfile
import io
import pandas as pd
from datetime import date
import streamlit as st
import requests
from io import BytesIO

# Estilo para tonos azules y logo
st.markdown(
    """
    <style>
    /* Cambiar el color de los radio buttons */
    div[data-baseweb="radio"] label {
        color: #005A9C !important; /* Azul oscuro */
    }
    
    /* Cambiar el color del fondo cuando se selecciona */
    div[data-baseweb="radio"] input:checked + div {
        background-color: #0078D7 !important; /* Azul claro */
        color: white !important;
    }

    /* Cambiar color de fondo de la barra lateral */
    section[data-testid="stSidebar"] {
        background-color: #D9EAF7 !important; /* Azul muy claro */
    }

    /* Cambiar color de los botones */
    button {
        background-color: #0078D7 !important; /* Azul */
        color: white !important;
    }
    button:hover {
        background-color: #005A9C !important; /* Azul más oscuro */
    }
    
    /* Cambiar el color del punto del radio button sin afectar el fondo del texto */
    [role="radiogroup"] > label > div:first-child {
    background-color: #005A9C !important;  /* Azul oscuro */
    border-color: #005A9C !important;  /* Azul oscuro */
    }

    /* Mantener el fondo del texto transparente */
    [role="radiogroup"] > label > div:nth-child(2) {
    background-color: transparent !important;
    }
             
    </style>
    """,
    unsafe_allow_html=True
)

# Agregar el logo
logo_path = "logo2.png"  # Cambia la ruta al archivo de tu logo
st.sidebar.image(logo_path, use_container_width=True)

# Tu código principal
st.title("INSTRUMENTO DE VERIFICACIÓN DE SERVICIO FARMACÉUTICO")

# Diccionario de operadores y NITs
operadores = {
    "SELECCIONAR": "---------------",
    "COHAN": "890985122",
    "GENHOSPI": "900331412",
    "INSUMEDIC": "900716566",
    "MEDICINA Y TECNOLOGIA EN SALUD MYT": "900057926",
    "SUMINISTROS Y DOTACIONES": "802000608",
    "DISFARMA": "900580962",
    "CRUZ VERDE": "800149695",
    "DISCOLMETS": "828002423",
    "HUMSALUD": "900994906",
    "ETICOS": "892300678",
    "JEZA": "901048992",
    "MEDISFARMA": "901148499",
    "DISTRIMEVD": "901433283",
    "CYA": "860029216",
    "AUDIFARMA": "816001182",
    "FARMACIA INST": "900285194",
    "INHAPRO": "901200716",
    "PHARMASAN": "900249425",
    "CLINICA EL CARMEN": "800149384",
    "VALENTECH PHARMA COLOMBIA SAS": "900677118",
    "LIGA CONTRA EL CANCER SECCIONAL RISARALDA": "891408586",
    "CENTRO ONCOLOGICO DE ANTIOQUIA SAS": "900236850",
    "UNIDAD HEMATO ONCOLOGICA Y DE RADIOTERAPIA DEL CARIBE": "900095504",
    "CLINICA LA ERMITA DE CARTAGENA": "900491883",
    "UNION TEMPORAL ONCOLOGICA ISNOOS SN": "901776252",
    "SANOFI AVENTIS DE COLOMBIA SA": "830010337",
    "NEXT PHARMA COLOMBIA SAS": "900382525",
    "EXELTIS SAS": "900716452",
    "FORPRESALUD": "804008792",
    "MACROMED": "830107855",
    "MEDYTEC": "900057926",
    "OFFIMEDICAS": "900098550",
    "ETTICOS": "892300678",
    "MULTICARE": "901671387"
}

# Inicializar variables de sesión
if "responses" not in st.session_state:
    st.session_state["responses"] = {}
if "consecutivo" not in st.session_state:
    st.session_state["consecutivo"] = 1
if "form" not in st.session_state:
    st.session_state["form"] = {}
if "load_form" not in st.session_state:
    st.session_state["load_form"]=False   
if 'Datos Generales' not in st.session_state:
    st.session_state['Datos Generales'] = {}

# Ruta de almacenamiento de formularios
folder_path = "formularios_guardados"
os.makedirs(folder_path, exist_ok=True)

def convertir_fecha(obj):
    if isinstance(obj, date):
        return obj.isoformat()  # Convierte a cadena 'YYYY-MM-DD'
    raise TypeError("Tipo no serializable")


# Función para guardar el estado actual del formulario
def guardar_estado():
    operador = st.session_state["form"].get("Operador", "SELECCIONAR")
    nit_operador = operadores.get(operador, "DESCONOCIDO")
    Nit_sucursal=farmacias_filtradas.get("Nit_sucursal:", datos_farmacia["COD. SUC"])
    fecha_auditoria = date.today().isoformat()
    consecutivo = f"{fecha_auditoria[:4]}_{st.session_state['consecutivo']}"
    Auditor = st.session_state["form"].get("Auditor 1")
    filename = f"Formulario_{Auditor}_{Nit_sucursal}_{consecutivo}.json"
    file_path = os.path.join(folder_path, filename)
    

    # Crear contenido JSON
    data = {
        "form": st.session_state["form"],
        "responses": st.session_state["responses"],
        "consecutivo": st.session_state["consecutivo"],
        "load_form": st.session_state["load_form"]
    }
    
    
    # Guardar en un archivo temporal para permitir la descarga
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4, default=convertir_fecha)

    st.session_state["consecutivo"] += 1
    st.success(f"Formulario guardado como: {filename}")

    # Botón para descargar
    with open(file_path, "r",encoding="utf-8") as file:
        st.download_button(
            label="Descargar formulario",
            data=file.read(),
            file_name=filename,
            mime="application/json",
        )

# Función para cargar formulario desde un archivo JSON basado en un consecutivo
def cargar_formulario_por_consecutivo(consecutivo_input):
    # Ahora la función acepta un argumento
    archivo_a_cargar = f"Formulario_{str(consecutivo_input)}.json"
    file_path = os.path.join(folder_path, archivo_a_cargar)

    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            # Actualizar session_state con los datos cargados
            st.session_state["Datos Generales"] = data.get("Datos Generales",{})
            st.session_state["form"] = data.get("form", {})
            st.session_state["responses"] = data.get("responses", {})
            st.session_state["consecutivo"] = data.get("consecutivo", 1)

            st.success(f"Formulario {archivo_a_cargar} cargado correctamente.")
        except Exception as e:
            st.error(f"Error al cargar el archivo: {e}")
    else:
        st.error(f"No se encontró un archivo con el consecutivo {consecutivo_input}.")


# Función para finalizar y generar el archivo TXT
def finalizar_formulario():
    operador = st.session_state["form"].get("Operador", "SELECCIONAR")
    nit_operador = operadores.get(operador, "DESCONOCIDO")
    Nit_sucursal=farmacias_filtradas.get("Nit_sucursal:", datos_farmacia["COD. SUC"])
    fecha_auditoria = date.today().isoformat()
    consecutivo = f"{fecha_auditoria[:4]}_{st.session_state['consecutivo']}"
    Auditor = st.session_state["form"].get("Auditor 1")
    filename = f"Formulario_{Auditor}_{Nit_sucursal}_{consecutivo}.txt"
    file_path = os.path.join(folder_path, filename)

  
     # Escribir cabecera
    Contenido = (
            "Operador,Nit operador,datos_farmacia,Nit_sucursal,ciudad,direccion,telefono,"
            "Nivel y Tipo de servicio farmacéutico,Representante legal,Director técnico,"
            "Auditor 1,Auditor 2,Tipo de Droguería,Fecha de Auditoria,Grupo de Pregunta,Subgrupo de pregunta,Respuesta,observacion,Valor\n"
        )
        
     # Escribir datos generales y respuestas
    for grupo, preguntas in st.session_state["responses"].items():
            for pregunta, respuesta in preguntas.items():
                Contenido +=(
                    f"{operador},{nit_operador},"
                    f"{st.session_state['form'].get('datos_farmacia', '')},"
                    f"{st.session_state['form'].get('Nit_sucursal', '')},"
                    f"{st.session_state['form'].get('ciudad', '')},"
                    f"{st.session_state['form'].get('direccion', '')},"
                    f"{st.session_state['form'].get('telefono', '')},"
                    f"{st.session_state['form'].get('Nivel y Tipo de servicio farmacéutico', '')},"
                    f"{st.session_state['form'].get('Representante legal', '')},"
                    f"{st.session_state['form'].get('Director técnico', '')},"
                    f"{st.session_state['form'].get('Auditor 1', '')},"
                    f"{st.session_state['form'].get('Auditor 2', '')},"
                    f"{st.session_state['form'].get('Fecha de Auditoria', '')},"
                    f"{st.session_state['form'].get('observacion', '')},"
                    f"{grupo},{pregunta},{respuesta['respuesta']},{respuesta['valor']}\n"
                )
    # Convertir el contenido a bytes
    Contenido_bytes = Contenido.encode("utf-8")
    
    #boton de descarga
    st.download_button(label="Descargar archivo txt",
                   data=Contenido,
                   file_name=filename,
                   mime="text/plain"
                   )

# Crear carpeta si no existe
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, filename)

# Crear contenido del archivo
    with open(file_path, "w") as file:
        # Escribir cabecera
        file.write(
            "Operador,Nit operador,datos_farmacia,Nit_sucursal,ciudad,direccion,telefono,"
            "Nivel y Tipo de servicio farmacéutico,Representante legal,Director técnico,"
            "Auditor 1,Auditor 2,Tipo de Droguería,Fecha de Auditoria,Grupo de Pregunta,Subgrupo de pregunta,Respuesta,observacion,Valor\n"
        )
        
        # Escribir datos generales y respuestas
        for grupo, preguntas in st.session_state["responses"].items():
            for pregunta, respuesta in preguntas.items():
                file.write(
                    f"{operador},{nit_operador},"
                    f"{st.session_state['form'].get('datos_farmacia', '')},"
                    f"{st.session_state['form'].get('Nit_sucursal', '')},"
                    f"{st.session_state['form'].get('ciudad', '')},"
                    f"{st.session_state['form'].get('direccion', '')},"
                    f"{st.session_state['form'].get('telefono', '')},"
                    f"{st.session_state['form'].get('Nivel y Tipo de servicio farmacéutico', '')},"
                    f"{st.session_state['form'].get('Representante legal', '')},"
                    f"{st.session_state['form'].get('Director técnico', '')},"
                    f"{st.session_state['form'].get('Auditor 1', '')},"
                    f"{st.session_state['form'].get('Auditor 2', '')},"
                    f"{st.session_state['form'].get('Fecha de Auditoria', '')},"
                    f"{st.session_state['form'].get('observacion', '')},"
                    f"{grupo},{pregunta},{respuesta['respuesta']},{respuesta['valor']}\n"
                )
           
    st.session_state["consecutivo"] += 1
    st.success(f"Formulario guardado como: {filename}")

# Función para reiniciar el formulario
def reiniciar_formulario():
    st.session_state["Datos Generales"] = {}
    st.session_state["responses"] = {}
    st.session_state["form"] = {}
    st.session_state["operador"] = "SELECCIONAR"
    st.session_state.clear()

# Función para cargar la base de datos desde un archivo Excel
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/JohanaSab/proyectos/main/DIRECTORIO_Operadores.xlsx"
    
    response = requests.get(url)
    if response.status_code == 200:
        excel_data = BytesIO(response.content)
        return pd.read_excel(excel_data, engine="openpyxl")  # 🔹 Ahora usa openpyxl
    
    else:
        st.error(f"❌ Error al descargar el archivo: {response.status_code}")
        return None

df = load_data()

if df is not None:
    st.write("✅ Datos cargados correctamente:")
    st.write(df)
else:
    st.warning("No se pudo cargar la base de datos.")
    
# Encabezado
st.title("")

# Barra lateral: Datos generales
st.sidebar.header("Datos Generales")
if "form" not in st.session_state:st.session_state["form"] = {}
# Seleccionar operador
operador = st.sidebar.selectbox("Operador", operadores.keys())

# Obtener el NIT del operador seleccionado correctamente
nit_operador = operadores.get(operador, "DESCONOCIDO")
st.session_state["form"]["Nit_operador"] = nit_operador
st.sidebar.write(f"NIT del Operador: {nit_operador}")

# Filtrar farmacias por NIT del operador
if nit_operador.isdigit():  # Verifica si el NIT es un número válido
    farmacias_filtradas = df[df["Nit"] == int(nit_operador)]
else:
    farmacias_filtradas = pd.DataFrame()

if not farmacias_filtradas.empty:
    # Lista desplegable con nombres de farmacias
    farmacia_seleccionada = st.sidebar.selectbox("Seleccione la farmacia:", farmacias_filtradas["NOMBRE DE LA FARMACIA"].unique())

    # Obtener datos de la farmacia seleccionada
    datos_farmacia = farmacias_filtradas[farmacias_filtradas["NOMBRE DE LA FARMACIA"] == farmacia_seleccionada].iloc[0]

    # Campos prellenados pero editables
    Nit_sucursal = st.sidebar.text_input("Nit_sucursal:", datos_farmacia["COD. SUC"])
    ciudad = st.sidebar.text_input("Ciudad:", datos_farmacia["CIUDAD / MUNICIPIO"])
    direccion = st.sidebar.text_input("Dirección:", datos_farmacia["DIRECCIÓN DE CONTACTO"])
    telefono = st.sidebar.text_input("Teléfono:", datos_farmacia["TELÉFONO DE CONTACTO"])
else:
    st.sidebar.warning("No se encontraron farmacias para este operador.")

# Otros campos editables
st.session_state["form"]["Nivel y Tipo de servicio farmacéutico"] = st.sidebar.text_input("Nivel y Tipo de servicio farmacéutico", value=st.session_state["form"].get("Nivel y Tipo de servicio farmacéutico", ""))
st.session_state["form"]["Representante legal"] = st.sidebar.text_input("Representante legal", value=st.session_state["form"].get("Representante legal", ""))
st.session_state["form"]["Director técnico"] = st.sidebar.text_input("Director técnico", value=st.session_state["form"].get("Director técnico", ""))
st.session_state["form"]["Auditor 1"] = st.sidebar.text_input("Auditor 1", value=st.session_state["form"].get("Auditor 1", ""))
st.session_state["form"]["Auditor 2"] = st.sidebar.text_input("Auditor 2", value=st.session_state["form"].get("Auditor 2", ""))
st.session_state["form"]["Fecha de Auditoria"] = st.sidebar.date_input("Fecha de Auditoria", value=pd.to_datetime(st.session_state["form"].get("Fecha de Auditoria", "2025-01-01")))
st.sidebar.radio(
    "Tipo de Droguería", ["Aliada", "Propia", "Otros"],
    key="tipo_drogueria",
    on_change=lambda: st.session_state["form"].update({"Tipo de Droguería": st.session_state["tipo_drogueria"]})
)
 
# Navegación entre grupos de preguntas
grupos = [
    "CONCEPTO NORMATIVO", "TALENTO HUMANO", "INFRAESTRUCTURA",
    "CONDICIONES LOCATIVAS", "DOTACION", "PROCESOS PRIORITARIOS",
    "GESTION DE LA CALIDAD", "APLICATIVOS TÉCNOLOGICOS (SISTEMA)"
]

grupo_actual = st.sidebar.radio("Navegación", grupos)

#Preguntas detalladas por grupo
preguntas_por_grupo = {
    "CONCEPTO NORMATIVO":["**1.1** Cuentan con RUT con actividad comercial correspondiente al tipo de establecimiento. (Ley 1607 de 2012)\n**Descripción:** Valide que cuente con RUT vigente y describe la actividad comercial de acuerdo al tipo de establecimiento",
                          "**1.2** N. Matricula mercantil vigente de la cámara de comercio de la respectiva jurisdicción. (Cámara de comercio renovada y actividad comercial ajustada al tipo de establecimiento). (Dec. 1879 de 2008)  \n**Descripción:** Valide que cuente con matricula mercantil vigente y que aparezca en la cámara de comercio",
                          "**1.3** Cuentan con certificados de uso de suelo expedido por planeación municipal.  \n**Descripción:** Valide el certificado de uso de suelo de acuerdo a lo indicado",
                          "**1.4** Cuentan con autorización de la secretaria seccional de salud y protección social departamental o regional para su funcionamiento (Acta de visita y/o sello de la secretaria)  \n**Descripción:** Valide el acta de autorización emitida por la secretaria seccional de salud y protección social para su funcionamiento, se debe registrar concepto y fecha de la visita, si el establecimiento no cuenta con acta debe contar con una carta de solicitud al momento de la apertura radicada al ente territorial según corresponda",
                          "**1.5** Cuenta con Resolución del Fondo Nacional de Estupefacientes (FNE), para la tenencia y manejo de medicamentos de control especial vigente.  \n**Descripción:** Verifique la resolución del Fondo Nacional de Estupefacientes (FNE) y su vigencia"
                          ],
    "TALENTO HUMANO":["**2.1** Cuenta con el talento humano necesario para la realización de las funciones de acuerdo con la constitución del establecimiento (Químico Farmacéutico, Regente de farmacia, Auxiliares técnicos en servicios farmacéuticos, etc), según sea el caso.  \n**Descripción:** El talento humano en salud, cuenta con la autorización expedida por la autoridad competente, para ejercer la profesión u ocupación.  \n**Soporte:** Resolución 1403 de 2007 - Capitulo 3; Capitulo 5 literal 1.4, 2.3",
                      "**2.2** En el área administrativa del servicio farmacéutico cuenta con la siguiente información de los empleados  \n**Descripción:** Validar que se cuente con el diploma ubicado en un lugar visible y que la hoja de vida se encuentre disponible en el servicio",
                      "**2.3** Cuenta con un cronograma de capacitaciones para los funcionarios con actas de asistencia.  \n**Descripción:** Solicite el cronograma de capacitaciones del último año, valide que se hayan realizado las capacitaciones y solicite el listado de participación."
                      ],
    "INFRAESTRUCTURA": ["**3.1** El servicio farmacéutico está ubicado en un lugar independiente o cualquier establecimiento comercial o habitación, con facilidad de acceso para los usuarios  \n**Descripción:** Está ubicado en área de fácil acceso y dimensiones determinadas por el volumen de actividades, el número y tipo de procesos y el número de trabajadores que laboren en el servicio.  \n**Soporte:** Resolución 1403 de 2007 - Capitulo 5; Literal 1.1.1",
                        "**3.2** Se identifica con aviso visible que exprese la razón o denominación social del establecimiento, ubicado en la parte exterior del establecimiento  \n**Descripción:** Verifique aviso al exterior del establecimiento donde se indique la razón o denominación del mismo.  \n**Soporte:** Resolución 1403 de 2007 - Capitulo 5; Información general",
                        "**3.3** Cuenta con unidades sanitarias correspondientes y necesarias de acuerdo al número y tipo de personas que laboran en el establecimiento.  \n**Descripción:** Verifique que cuente con las unidades sanitarias en adecuadas condiciones de mantenimiento, orden y limpieza, usada para el fin dispuesto, en proporción al número de personas que laboran en el establecimiento.  \n**Soporte:** Resolución 1403 de 2007 - Capitulo 5 literal 1.1.3"
                        ],
    "CONDICIONES LOCATIVAS": ["**4.1** Los pisos, paredes y techos de todos los servicios deberán ser de fácil limpieza y estar en buenas condiciones de presentación y mantenimiento.  \n**Descripción:** Verifique que los pisos y paredes sean de materiales impermeables de fácil limpieza, resistentes a factores ambientales y sistema de drenaje para su fácil limpieza y sanitación.  \n**Soporte:** Resolución 1403 de 2007 - Titulo 1 - Capitulo 2 literal 1 (Infraestructura física)",
                              "**4.2** Posee un sistema de ventilación natural y/o artificial que garantice la conservación adecuada de los medicamentos y dispositivos médicos.  \n**Descripción:** Valide que cuente con ventilación natural o artificial que garantice las condiciones adecuadas del almacenamiento de los medicamentos, recuerde que no puede haber interferencia ambiental externa dentro de los espacios (ventanas abiertas, rejillas de aire, etc)  \n**Soporte:** Resolución 1403 de 2007 - Titulo 1 - Capitulo 2 literal 1 (Infraestructura física)",
                              "**4.3** Cuenta con sistema de iluminación natural o artificial para la adecuada realización de las actividades  \n**Descripción:** Valide que la iluminación sea adecuada en número e intensidad de luz para la dispensación y su correcto funcionamiento.  \n**Soporte:** Resolución 1403 de 2007 - Titulo 1 - Capitulo 2 literal 1 (Infraestructura física)",
                              "**4.4** Cuenta con tomas, interruptores y cableado protegido.  \n**Descripción:** Validar que las instalaciones eléctricas como tomas, interruptores y cableado electrico y de datos esten protegidos y en buen estado.  \n**Soporte:** Resolución 1403 de 2007 - Titulo 1 - Capitulo 2 literal 1 (Infraestructura física)",
                              "**4.5** Se evidencian aviso exterior e interior de: horario de atención, informativos de “Espacio libre de humo de cigarrillo”, “Requisitos de la formula Medica” y “acceso restringido al personal ajeno a la farmacia”  \n**Descripción:** Valide si se evidencia horario de atención al público  \n**Soporte:** Resolución 1403 de 2007 - Titulo 1 - Capitulo 3, literal 1.7",
                              "**4.6** El establecimiento tiene identificadas y señalizadas las rutas de evacuación, las salidas de emergencia y en términos generales cada una de sus áreas en caso de accidentes  \n**Descripción:** Valide que se encuentre visible el mapa de ruta de evacuación para el punto y valide que se encuentren señalizadas las rutas según el mismo.  \n**Soporte:** NTC 1461",
                              "**4.7** El establecimiento cuenta con alertas de control de temperatura   \n**Descripción:** Revisar la temperatura mínima y máxima registrada en el equipo y solicitar justificación en caso de encontrarse desviaciones. Para casos en los que se cuente con sensor netux abra la nevera y espere a que se encuentre a más de 8°C, valide que se active la alerta de temperatura fuera de rango.",
                              "**4.8** En las áreas de almacenamiento de medicamentos y dispositivos médicos cuenta con alarmas sensibles al humo y extintores de incendios. En éstas no se podrán acumular residuos.  \n**Descripción:** Verifique la disposición de alarmas sensibles al humo y extintores, además verifique que cuentan con extintores en funcionamiento, ubicados de acuerdo a las normas de seguridad, con fecha vigente de recarga y señalizada la ubicación.  \n**Soporte:** Resolución 1403 de 2007 - Titulo 2 Capitulo 2, literal 3.2",
                              "**4.9** Cuenta con las áreas requeridas para la realización de los procesos del establecimiento. Diferentes para cada proceso, diferenciadas y debidamente señalizadas  \n**Descripción:** Verifique que cuenta con las áreas de: Área administrativa debidamente delimitada o señalizada con rotulo de identificación.  \n**Soporte:** Resolución 1403 de 2007 - Titulo 1 - Capitulo 5, literal 1,1,2",
                              "**4.10** Las instalaciones se mantienen en condiciones adecuadas de conservación higiene y limpieza  \n**Soporte:** Resolución 1403 de 2007 - Titulo 1 - Capitulo 5, literal 1,6,3",
                              "**4.11** Área de aseo, donde se encuentre los implementos para la adecuada higienización  \n**Descripción:** Verifique que los desechos son clasificados en su fuente de generación según el código de colores: Blanca y negra  \n**Soporte:** Resolución 2184 de 2019 / Resolución 1344 de 2020",
                              "**4.12** Lista de chequeo con frecuencias de desinfección y limpieza de áreas  \n**Descripción:** Valide la lista de chequeo con frecuencias de desinfección y limpieza de áreas",
                              "**4.13** Manejo y disposición de residuos  \n**Descripción:** El establecimiento cuenta con el plan de gestión integral de residuos sólidos (ordinarios)  \n**Soporte:** Resolución 754 de 2014"
                              ],
    "DOTACION": ["**5.1** Cuenta con la dotación y muebles exclusivos y necesarios para la adquisición, recepción, almacenamiento, conservación (como manejo de cadena de frio, medicamentos fotosensibles, higroscópicos entre otros) y dispensacion de los medicamentos y dispositivos médicos para la realización de los procesos que ofrezcan, de acuerdo con las recomendaciones dadas por los fabricantes, además de las condiciones de temperatura y humedad, registro de condiciones ambientales, termo higrómetros calibrados  \n**Descripción:** Verifique que cuenta con estantería de material sanitario, impermeable y fácil de limpiar. (estibas plásticas, no de madera) suficiente para el almacenamiento de los medicamentos de acuerdo a su condición y cantidad   \n**Soporte:** Resolución 1403 de 2007 - Titulo 2 Capitulo 2, literal 3",
                 "**5.2** Corresponde a Pregunta 5.1  \n**Descripción:** Cuenta con equipos para la medición de condiciones de temperatura y humedad y los mismos se encuentran en funcionamiento y calibrados.  \nSolicite las hojas de vida y las certificados de calibración. Valide que la empresa de calibración se encuentre certificada por la ONAC.  \nSolicite el cronograma de mantenimiento y certificados de los equipos refrigerantes.",
                 "**5.3** Corresponde a Pregunta 5.1  \n**Descripción:** Solicite los registros de condiciones de temperatura y humedad, verifique los datos actualizados y que se encuentren en los niveles de seguridad establecidos, en caso de tener algún dato fuera del rango solicite la acción correctiva realizada para el caso.",
                 "**5.4** Se evidencia equipos e implementos de seguridad en funcionamiento y ubicados donde tengan fácil acceso (extintores, barandas, estibas, extractoras)  \n**Descripción:** Cuentan con extintores en funcionamiento, ubicados de acuerdo a las normas de seguridad, con fecha vigente de recarga y señalizada su ubicación  \n**Soporte:** Resolución 1403 de 2007 - Titulo 2 Capitulo 2, literal 3.2",
                 "**5.5** Cuenta con los equipos necesarios para cumplir con el plan de contingencia, en caso de falla eléctrica para mantener la cadena de frío.  \n**Descripción:** Valide el plan de contingencia que se tiene implementado en caso de falla de temperatura y verifique que se cuente con los insumos necesarios para esta acción.  \n**Soporte:** Resolución 1403 de 2007 - Titulo 2 Capitulo 2, literal 3,2",
                 "**5.6** Cuenta con medios refrigerantes para el almacenamiento de medicamentos que lo requieren  \n**Descripción:** Verifique que las neveras sean de uso exclusivo para almacenamiento de los medicamentos que lo requieren  \n**Soporte:** Resolución 1403 de 2007 - Titulo 2 capitulo 2, literal 3 (Recepción y almacenamiento de medicamentos y dispositivos médicos)",
                 "**5.7** Cuenta con literatura científica disponible y aceptada internacionalmente;  referencias bibliográficas actualizadas y confiables sobre farmacología y farmacoterapia para su consulta  \n**Soporte:** Resolución 1403 de 2007 - Titulo 1 - Capitulo 5, literal 1.2",
                 "**5.8** Cuenta con Kit de manejo de derrames y ruptura de medicamentos  \n**Descripción:** Verifique que este kit se encuentre completo para su uso.  \n**Soporte:** Resolución 3100/2019"
                 ],
    "PROCESOS PRIORITARIOS": ["**6.1** Recepción  \n**Descripción:** Solicite el documento del proceso de recepción técnica administrativa de medicamentos, indague como se realiza y valide en las actas su correcta ejecución.  \n**Soporte:** Resolución 1403 de 2007 - Titulo 2 capitulo 2, literal 3 (Recepción y almacenamiento de medicamentos y dispositivos médicos)",
                              "**6.1.1** Recepción  \n**Descripción:** En caso que transporten medicamentos y dispositivos médicos a otras sedes o sucursales, verifican las condiciones en que son transportados y llevan registro de dicho procedimiento (documento soporte de traslado)  \n**Soporte:** Resolución 1403 de 2007 - Titulo 2 capitulo 2, literal 3 (Recepción y almacenamiento de medicamentos y dispositivos médicos)",
                              "**6.1.2** Recepción  \n**Descripción:** Se realiza la identificación y marcación de medicamentos lasa y alto riesgo  \n**Soporte:** Resolución 1403 de 2007 - Titulo 2 capitulo 2, literal 3 (Recepción y almacenamiento de medicamentos y dispositivos médicos)",
                              "**6.1.3** Recepción  \n**Descripción:** Se tienen en cuenta las condiciones dadas por el fabricante para el almacenamiento de medicamentos y dispositivos médicos  \n**Soporte:** Resolución 1403 de 2007 - Titulo 2 capitulo 2, literal 3 (Recepción y almacenamiento de medicamentos y dispositivos médicos)",
                              "**6.1.4** Recepción  \n**Descripción:** Verificar el procedimiento de recepción de medicamentos y dispositivos médicos que llegan del CEDI a las droguerías, verificando mantenimiento de la cadena de frio y condiciones de embalaje.  \n**Soporte:** Resolución 1403 de 2007 - Titulo 2 capitulo 2, literal 3 (Recepción y almacenamiento de medicamentos y dispositivos médicos)",
                              "**6.2** Almacenamiento  \n**Descripción:** Solicite el documento del proceso de almacenamiento y valide que se realice en la manera descrita, tener en cuenta que debe ser acuerdo a un método de clasificación (alfabéticamente, forma farmacéutica, otros) y los dispositivos médicos deben almacenarse de acuerdo a lo establecido, siempre y cuando garantice el orden y minimice eventos de confusión.  \n**Soporte:** Resolución 1403 de 2007 - Titulo 2 capitulo 2, literal 3 (Recepción y almacenamiento de medicamentos y dispositivos médicos)",
                              "**6.2.1** Almacenamiento  \n**Descripción:** El establecimiento está libre de productos farmacéuticos prohibidos (medicamentos de control especial sin autorización, vencidos en el área de dispensación, muestras médicas, productos con enmendaduras o etiquetas que oculten información, sin registro sanitario, con el sistema de seguridad alterado, entre otros).  \n**Soporte:** Art 77, Dec 677/95. Art 45, Dec 3554/04.",
                              "**6.2.2** Almacenamiento  \n**Descripción:** Solicite el proceso de control de fechas de vencimiento de medicamentos y valide que se lleve a cabo y que los auxiliares lo conozcan. Adicionalmente valide que no haya medicamentos vencidos ubicados en las estanterías de suministro.  \n**Soporte:** Resolución 1403 de 2007 - Titulo 2 capitulo 2, literal 3 (Recepción y almacenamiento de medicamentos y dispositivos médicos)",
                              "**6.3** Medicamentos de control especial  \n**Descripción:** Verifique que el área para el almacenamiento de los medicamentos de control especial sea independiente, diferenciada, señalizada y se encuentra bajo llave en área de acceso restringido al público general. Solo el director técnico debe tener acceso, debe solicitarse el soporte que delega la responsabilidad a los auxiliares para cuando no esté el director técnico y debe especificar nombre y cedula del responsable.  \n**Soporte:** Resolución 1478 de 2006",
                              "**6.3.1** Medicamentos de control especial  \n**Descripción:** Cumple con la presentación de informe al FNE dentro de las fechas establecidas. (Validar en ciudades fuera de Bogotá y Cundinamarca estas se validarán a nivel central)  \n**Soporte:** Resolución 1478 de 2006",
                              "**6.3.2** Medicamentos de control especial  \n**Descripción:** Tome al menos 10 medicamentos aleatoriamente y valide las existencias Vs documento de control de dispensación (libro). Debe coincidir la existencia física Vs lo reportado en el libro.  \n**Soporte:** Resolución 1478 de 2006",
                              "**6.4** Dispensación  \n**Descripción:** Solicite el documento con el proceso de dispensación de medicamentos y dispositivos médicos y otros productos farmacéuticos, valide que se esté ejecutando de acuerdo a lo descrito.  \n**Soporte:** Resolución 1403 de 2007 - Titulo 2 capitulo 2, literal 5 (Dispensación de medicamentos)",
                              "**6.4.1** Dispensación  \n**Descripción:** Valide que se esté colocando el sello de dispensado en los medicamentos de control especial",
                              "**6.4.2** Dispensación  \n**Descripción:** Verifique aleatoriamente si al paciente no se le realiza entrega completa de la orden medica por algún medicamento que no cuenta con novedad en inventario, que a este se le genere el pendiente en sistema y se le ofrezca el envío a domicilio del mismo. Llevar consigo la última versión del informe de novedades.  \n**Soporte:** Resolución 1403 de 2007 - Titulo 2 capitulo 2, literal 5 (Dispensación de medicamentos); resolución 1604/2013",
                              "**6.5** Atención farmacéutica  \n**Descripción:** Validar que la asesoría farmacológica no se este dando por parte de personal  diferente al químico farmacéutico   \n**Soporte:** Resolución 1403 de 2007 - Titulo 2 - Capitulo 3; resolucion 1604/2013",
                              "**6.6** Errores de medicación, Farmacovigilancia y Tecnovigilancia  \n**Descripción:** Los funcionarios de la droguería conoce los programas de farmacovigilancia, tecnovigilancia institucionales y errores de medicación.  \n**Soporte:** Resolución 1403 de 2007 - Titulo 2 - Capitulo 3 Resolución 2004009455 de 2006 Decreto 2200 de 2005 Resolución 4826 de 2008",
                              "**6.7** Alertas sanitarias  \n**Descripción:** Verifique si se realiza la socialización de las alertas Sanitarias al personal de la farmación emitidas por los entes regulatorios."
                              ],
    "GESTION DE LA CALIDAD": ["**7.1** Cuenta con visitas de entes de control con algún tipo de hallazgos y los mismos ya se encuentran solventados  \n**Descripción:** Valide con soporte físico la útlima visita de entes de control y verifique si hay requerimientos y los mismos ya se encuentran solventados  \n**Soporte:** Resolución 1403 - Titulo 1 - Capitulo 4",
                             "**7.2** Realizan inventario (periódico, trimestral o semestral)  \n**Descripción:** Solicite el inventario con su última actualización.  \n**Soporte:** Resolución 1403 - Titulo 1 - Capitulo 4",
                             "**7.3** Evaluación y seguimiento a la dispensación  \n**Descripción:** La institución cuenta con actividades de seguimiento a la adherencia del procedimiento de dispensación de medicamentos a los auxiliares de farmacia. (Metodo observacional)  \n**Soporte:** Modelo operativo dispensación de medicamentos",
                             "**7.4** Establecimiento cuenta con matriz de riesgo y la misma es de conocimiento por parte de los funcionarios  \n**Descripción:** Solicitar la matriz de riesgo y validar que los funcionarios la conozcan.  \n**Soporte:** Resolución 1403 - Titulo 1 - Capitulo 4"
                             ],
    "APLICATIVOS TÉCNOLOGICOS (SISTEMA)": ["**8.1** Cuenta con medios, preferiblemente computarizados que permitan el registro de adecuado de formulas prescritas, medicamentos de control especial y demas productos que lo requieran  \n**Descripción:** Verificar el sistema que manejan en el punto, su correcto funcionamiento y utilización.  \n**Soporte:**   Resolución 1403 de 2007 - Titulo 1 - Capitulo 5, literal 1.2",
                                           "**8.2** Corresponde a pregunta anterior  \n**Descripción:** Validar de manera aleatoria en el informe de novedades que los medicamentos que presentan novedad (desabastecidos) se encuentran bloqueados en el aplicativo de dispensación CYGNUS.Validar para los casos en los que no cuenta con disponibilidad en el punto la generación del pendiente en el sistema CYGNUS."
                                           ]
    }

# Mostrar preguntas del grupo actual
st.header(grupo_actual)
preguntas = preguntas_por_grupo.get(grupo_actual,[])

# Crear estructura de almacenamiento si no existe
if grupo_actual not in st.session_state["responses"]:
    st.session_state["responses"][grupo_actual] = {}

for pregunta in preguntas:
    if pregunta not in st.session_state["responses"][grupo_actual]:
        st.session_state["responses"][grupo_actual][pregunta] = {
            "respuesta": None,
            "valor": None,
            "observacion": "",
        }
        
       
        
    #respuestas seleccionadas previamente
    respuesta_actual = st.session_state["responses"][grupo_actual][pregunta].get("respuesta","Seleccione una opcion")
    observacion_actual = st.session_state["responses"][grupo_actual][pregunta].get("observacion","")

    #si no hay respuesta mostrar una opcion vacia para obligar la seleccion
    Opciones = ["Selecciona una opción","Cumple totalmente", "Cumple parcialmente", "Incumple totalmente"]

    # Mostrar la pregunta y permitir selección
    respuesta = st.radio(
        pregunta,
        Opciones,
        key=f"respuesta_{grupo_actual}_{pregunta}",
        index = Opciones.index(respuesta_actual) if respuesta_actual in Opciones else 0
        )
    
    #Campo de observacion
    observacion = st.text_area(f"Observacion",
                               value=observacion_actual,
                               key=f"Observacion_{grupo_actual}_{pregunta}",
                               on_change=lambda p=pregunta: actualizar_observacion(grupo_actual,p)
                               )
    def actualizar_observacion(grupo,pregunta):
        """Actualizar la observacion en session_state al escribir en el campo de texto."""
        clave = f"Observacion_{grupo}_{pregunta}"
        st.session_state["responses"][grupo][pregunta]["Observacion"] = st.session_state[clave]
        
    # Guardar respuesta y valor
    if respuesta != "Selecciona una opción":
            valor = 100 if respuesta == "Cumple totalmente" else 50 if respuesta == "Cumple parcialmente" else 0
            if grupo_actual not in st.session_state["responses"]:
                st.session_state["responses"][grupo_actual] = {}
            st.session_state["responses"][grupo_actual][pregunta] = {
            "respuesta": respuesta,
            "valor": valor,
            "Observacion": st.session_state[f"Observacion_{grupo_actual}_{pregunta}"]  # Usar el estado guardado
    }
   

# Calcular promedio
    total_valores = sum(
        r["valor"] if r ["valor"] is not None else 0 for g in st.session_state["responses"].values() for r in g.values()
)
num_preguntas = sum(len(g) for g in st.session_state["responses"].values())

#asegurar que el promedio sea sobre 100
promedio = (total_valores / (num_preguntas*100)) *100 if num_preguntas > 0 else 0

st.sidebar.metric("Promedio Total", round(promedio,2))

# Botones
st.sidebar.button("Finalizar y Enviar", on_click=finalizar_formulario)
st.sidebar.button("Nuevo formulario", on_click=reiniciar_formulario)
st.sidebar.button("Guardar", on_click=guardar_estado)

# Entrada de usuario
consecutivo_input = st.sidebar.text_input("Ingrese el código del formulario a cargar:")

# Botón para cargar el formulario
if st.sidebar.button("Cargar formulario"):
    if consecutivo_input:
        # Indicar que se debe cargar el formulario
        st.session_state["load_form"] = True
        st.session_state["input_consecutivo"] = consecutivo_input
    else:
        st.error("Por favor, ingrese un código de formulario válido.")

# Cargar el formulario si se indicó
if st.session_state.get("load_form"):
    consecutivo_input = st.session_state.get("input_consecutivo")
    cargar_formulario_por_consecutivo(consecutivo_input)  # Llamada correcta pasando el argumento
    st.session_state["load_form"] = False  # Restablecer el indicador

import streamlit as st
import os
import json
import tempfile

# Diccionario de operadores y NITs
operadores = {
    "SELECCIONAR": "---------------",
    "COHAN": "890985122",
    "GENHOSPI": "900331412",
    "INSUMEDIC": "900716566",
    "MYT": "900057926",
    "SUMINISTROS Y DOTACIONES": "802000608",
    "DISFARMA": "900580962",
    "CV": "800149695",
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

# Ruta de almacenamiento de formularios
folder_path = "formularios_guardados"
os.makedirs(folder_path, exist_ok=True)

# Función para guardar el estado actual del formulario
def guardar_estado():
    operador = st.session_state["form"].get("Operador", "SELECCIONAR")
    nit_operador = operadores.get(operador, "DESCONOCIDO")
    fecha_auditoria = st.session_state["form"].get("Fecha de Auditoria", "2025")
    consecutivo = f"{fecha_auditoria[:4]}_{st.session_state['consecutivo']}"
    Auditor = st.session_state["form"].get("Auditor (es)", "--")
    filename = f"Formulario_{Auditor}_{nit_operador}_{consecutivo}.json"
    file_path = os.path.join(folder_path, filename)

    # Crear contenido JSON
    data = {
        "form": st.session_state["form"],
        "responses": st.session_state["responses"],
        "consecutivo": st.session_state["consecutivo"],
    }
    
    # Guardar en un archivo temporal para permitir la descarga
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

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
            st.session_state["form"] = data.get("form", {})
            st.session_state["responses"] = data.get("responses", {})
            st.session_state["consecutivo"] = data.get("consecutivo", 1)

            st.success(f"Formulario {archivo_a_cargar} cargado correctamente.")
        except Exception as e:
            st.error(f"Error al cargar el archivo: {e}")
    else:
        st.error(f"No se encontró un archivo con el consecutivo {consecutivo_input}.")

# Entrada de usuario
consecutivo_input = st.text_input("Ingrese el código del formulario a cargar:")

# Botón para cargar el formulario
if st.button("Cargar formulario"):
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

# Función para finalizar y generar el archivo TXT
def finalizar_formulario():
    operador = st.session_state["form"].get("Operador", "SELECCIONAR")
    nit_operador = operadores[operador]
    fecha_auditoria = st.session_state["form"].get("Fecha de Auditoria", "2025")
    consecutivo = f"{fecha_auditoria[:4]}_{st.session_state['consecutivo']}"
    filename = f"Seguimiento_{nit_operador}_{consecutivo}.txt"
    file_path = os.path.join(folder_path, filename)


    # Crear carpeta si no existe
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, filename)

    # Crear contenido del archivo
    with open(file_path, "w") as file:
        # Escribir cabecera
        file.write(
            "Operador,Nit operador,Nombre de la droguería o farmacia,Nit,Ciudad,Dirección,Teléfono,"
            "Nivel y Tipo de servicio farmacéutico,Representante legal,Director técnico,"
            "Auditor (es),Tipo de Droguería,Fecha de Auditoria,Grupo de Pregunta,Subgrupo de pregunta,Respuesta,Valor\n"
        )
        
        # Escribir datos generales y respuestas
        for grupo, preguntas in st.session_state["responses"].items():
            for pregunta, respuesta in preguntas.items():
                file.write(
                    f"{operador},{nit_operador},"
                    f"{st.session_state['form'].get('Nombre de la droguería o farmacia', '')},"
                    f"{st.session_state['form'].get('Nit', '')},"
                    f"{st.session_state['form'].get('Ciudad', '')},"
                    f"{st.session_state['form'].get('Dirección', '')},"
                    f"{st.session_state['form'].get('Teléfono', '')},"
                    f"{st.session_state['form'].get('Nivel y Tipo de servicio farmacéutico', '')},"
                    f"{st.session_state['form'].get('Representante legal', '')},"
                    f"{st.session_state['form'].get('Director técnico', '')},"
                    f"{st.session_state['form'].get('Auditor (es)', '')},"
                    f"{st.session_state['form'].get('Fecha de Auditoria', '')},"
                    f"{grupo},{pregunta},{respuesta['respuesta']},{respuesta['valor']}\n"
                )
    
    st.session_state["consecutivo"] += 1
    st.success(f"Formulario guardado como: {filename}")

# Función para reiniciar el formulario
def reiniciar_formulario():
    st.session_state["responses"] = {}
    st.session_state["form"] = {}
    st.session_state["operador"] = "SELECCIONAR"
    st.session_state.clear()

# Encabezado
st.title("Seguimiento Operadores")

# Barra lateral: Datos generales
st.sidebar.header("Datos Generales")
operador = st.sidebar.selectbox(
    "Operador",
    operadores.keys(),
    key="operador",
    on_change=lambda: st.session_state["form"].update({"Operador": st.session_state["operador"]})
)

# Mostrar el NIT del operador seleccionado
nit_operador = operadores[operador]
st.sidebar.write(f"NIT del Operador: *{nit_operador}*")
st.session_state["form"]["NIT Operador"] = nit_operador

# Otros campos de datos generales
st.sidebar.text_input("Nombre de la droguería o farmacia", key="drogueria", on_change=lambda: st.session_state["form"].update({"Nombre de la droguería o farmacia": st.session_state["drogueria"]}))
st.sidebar.text_input("Nit", key="nit", on_change=lambda: st.session_state["form"].update({"Nit": st.session_state["nit"]}))
st.sidebar.text_input("Ciudad", key="ciudad", on_change=lambda: st.session_state["form"].update({"Ciudad": st.session_state["ciudad"]}))
st.sidebar.text_input("Dirección", key="direccion", on_change=lambda: st.session_state["form"].update({"Dirección": st.session_state["direccion"]}))
st.sidebar.text_input("Teléfono", key="telefono", on_change=lambda: st.session_state["form"].update({"Teléfono": st.session_state["telefono"]}))
st.sidebar.text_input("Nivel y Tipo de servicio farmacéutico", key="nivel_tipo", on_change=lambda: st.session_state["form"].update({"Nivel y Tipo de servicio farmacéutico": st.session_state["nivel_tipo"]}))
st.sidebar.text_input("Representante legal", key="representante", on_change=lambda: st.session_state["form"].update({"Representante legal": st.session_state["representante"]}))
st.sidebar.text_input("Director técnico", key="director", on_change=lambda: st.session_state["form"].update({"Director técnico": st.session_state["director"]}))
st.sidebar.text_input("Auditor (es)", key="auditor", on_change=lambda: st.session_state["form"].update({"Auditor (es)": st.session_state["auditor"]}))
st.sidebar.date_input("Fecha de Auditoria", key="fecha", on_change=lambda: st.session_state["form"].update({"Fecha de Auditoria": str(st.session_state["fecha"])}))
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
    "CONCEPTO NORMATIVO":["1.1 Cuentan con RUT con actividad comercial correspondiente al tipo de establecimiento. (Ley 1607 de 2012)_________Descripción: Valide que cuente con RUT vigente y describe la actividad comercial de acuerdo al tipo de establecimiento",
                          "1.2 N. Matricula mercantil vigente de la cámara de comercio de la respectiva jurisdicción. (Cámara de comercio renovada y actividad comercial ajustada al tipo de establecimiento). (Dec. 1879 de 2008)_________Descripción: Valide que cuente con matricula mercantil vigente y que aparezca en la cámara de comercio",
                          "1.3 Cuentan con certificados de uso de suelo expedido por planeación municipal._________Descripción: Valide el certificado de uso de suelo de acuerdo a lo indicado",
                          "1.4 Cuentan con autorización de la secretaria seccional de salud y protección social departamental o regional para su funcionamiento (Acta de visita y/o sello de la secretaria)_________Descripción: Valide el acta de autorización emitida por la secretaria seccional de salud y protección social para su funcionamiento, se debe registrar concepto y fecha de la visita, si el establecimiento no cuenta con acta debe contar con una carta de solicitud al momento de la apertura radicada al ente territorial según corresponda",
                          "1.5 Cuenta con Resolución del Fondo Nacional de Estupefacientes (FNE), para la tenencia y manejo de medicamentos de control especial vigente._________Descripción: Verifique la resolución del Fondo Nacional de Estupefacientes (FNE) y su vigencia"
                          ],
    "TALENTO HUMANO":["2.1 Cuenta con el talento humano necesario para la realización de las funciones de acuerdo con la constitución del establecimiento (Químico Farmacéutico, Regente de farmacia, Auxiliares técnicos en servicios farmacéuticos, etc), según sea el caso._________Descripción: El talento humano en salud, cuenta con la autorización expedida por la autoridad competente, para ejercer la profesión u ocupación.//Soporte: Resolución 1403 de 2007 - Capitulo 3; Capitulo 5 literal 1.4, 2.3",
                      "2.2 En el área administrativa del servicio farmacéutico cuenta con la siguiente información de los empleados_________Descripción: Validar que se cuente con el diploma ubicado en un lugar visible y que la hoja de vida se encuentre disponible en el servicio",
                      "2.3 Cuenta con un cronograma de capacitaciones para los funcionarios con actas de asistencia._________Descripción: Solicite el cronograma de capacitaciones del último año, valide que se hayan realizado las capacitaciones y solicite el listado de participación."
                      ],
    "INFRAESTRUCTURA": ["3.1 El servicio farmacéutico está ubicado en un lugar independiente o cualquier establecimiento comercial o habitación, con facilidad de acceso para los usuarios_________Descripción: Está ubicado en área de fácil acceso y dimensiones determinadas por el volumen de actividades, el número y tipo de procesos y el número de trabajadores que laboren en el servicio.//Soporte: Resolución 1403 de 2007 - Capitulo 5; Literal 1.1.1",
                        "3.2 Se identifica con aviso visible que exprese la razón o denominación social del establecimiento, ubicado en la parte exterior del establecimiento_________Descripción: Verifique aviso al exterior del establecimiento donde se indique la razón o denominación del mismo.//Soporte: Resolución 1403 de 2007 - Capitulo 5; Información general",
                        "3.3 Cuenta con unidades sanitarias correspondientes y necesarias de acuerdo al número y tipo de personas que laboran en el establecimiento._________Descripción: Verifique que cuente con las unidades sanitarias en adecuadas condiciones de mantenimiento, orden y limpieza, usada para el fin dispuesto, en proporción al número de personas que laboran en el establecimiento.//Soporte: Resolución 1403 de 2007 - Capitulo 5 literal 1.1.3"
                        ],
    "CONDICIONES LOCATIVAS": ["4.1 Los pisos, paredes y techos de todos los servicios deberán ser de fácil limpieza y estar en buenas condiciones de presentación y mantenimiento._________Descripción: Verifique que los pisos y paredes sean de materiales impermeables de fácil limpieza, resistentes a factores ambientales y sistema de drenaje para su fácil limpieza y sanitación.//Soporte: Resolución 1403 de 2007 - Titulo 1 - Capitulo 2 literal 1 (Infraestructura física)",
                              "4.2 Posee un sistema de ventilación natural y/o artificial que garantice la conservación adecuada de los medicamentos y dispositivos médicos._________Descripción: Valide que cuente con ventilación natural o artificial que garantice las condiciones adecuadas del almacenamiento de los medicamentos, recuerde que no puede haber interferencia ambiental externa dentro de los espacios (ventanas abiertas, rejillas de aire, etc)//Soporte: Resolución 1403 de 2007 - Titulo 1 - Capitulo 2 literal 1 (Infraestructura física)",
                              "4.3 Cuenta con sistema de iluminación natural o artificial para la adecuada realización de las actividades_________Descripción: Valide que la iluminación sea adecuada en número e intensidad de luz para la dispensación y su correcto funcionamiento.//Soporte: Resolución 1403 de 2007 - Titulo 1 - Capitulo 2 literal 1 (Infraestructura física)",
                              "4.4 Cuenta con tomas, interruptores y cableado protegido._________Descripción: Validar que las instalaciones eléctricas como tomas, interruptores y cableado electrico y de datos esten protegidos y en buen estado.//Soporte: Resolución 1403 de 2007 - Titulo 1 - Capitulo 2 literal 1 (Infraestructura física)"
                              "4.5 Se evidencian aviso exterior e interior de: horario de atención, informativos de “Espacio libre de humo de cigarrillo”, “Requisitos de la formula Medica” y “acceso restringido al personal ajeno a la farmacia”_________Descripción: Valide si se evidencia horario de atención al público//Soporte: Resolución 1403 de 2007 - Titulo 1 - Capitulo 3, literal 1.7",
                              "4.6 El establecimiento tiene identificadas y señalizadas las rutas de evacuación, las salidas de emergencia y en términos generales cada una de sus áreas en caso de accidentes_________Descripción: Valide que se encuentre visible el mapa de ruta de evacuación para el punto y valide que se encuentren señalizadas las rutas según el mismo.//Soporte: NTC 1461",
                              "4.7 El establecimiento cuenta con alertas de control de temperatura _________Descripción: Revisar la temperatura mínima y máxima registrada en el equipo y solicitar justificación en caso de encontrarse desviaciones. Para casos en los que se cuente con sensor netux abra la nevera y espere a que se encuentre a más de 8°C, valide que se active la alerta de temperatura fuera de rango.",
                              "4.8 En las áreas de almacenamiento de medicamentos y dispositivos médicos cuenta con alarmas sensibles al humo y extintores de incendios. En éstas no se podrán acumular residuos._________Descripción: Verifique la disposición de alarmas sensibles al humo y extintores, además verifique que cuentan con extintores en funcionamiento, ubicados de acuerdo a las normas de seguridad, con fecha vigente de recarga y señalizada la ubicación.//Soporte: Resolución 1403 de 2007 - Titulo 2 Capitulo 2, literal 3.2",
                              "4.9 Cuenta con las áreas requeridas para la realización de los procesos del establecimiento. Diferentes para cada proceso, diferenciadas y debidamente señalizadas_________Descripción: Verifique que cuenta con las áreas de: Área administrativa debidamente delimitada o señalizada con rotulo de identificación.//Soporte: Resolución 1403 de 2007 - Titulo 1 - Capitulo 5, literal 1,1,2",
                              "4.10 Las instalaciones se mantienen en condiciones adecuadas de conservación higiene y limpieza//Soporte: Resolución 1403 de 2007 - Titulo 1 - Capitulo 5, literal 1,6,3",
                              "4.11 Área de aseo, donde se encuentre los implementos para la adecuada higienización_________Descripción: Verifique que los desechos son clasificados en su fuente de generación según el código de colores: Blanca y negra//Soporte: Resolución 2184 de 2019 / Resolución 1344 de 2020",
                              "4.12 Lista de chequeo con frecuencias de desinfección y limpieza de áreas_________Descripción: Valide la lista de chequeo con frecuencias de desinfección y limpieza de áreas",
                              "4.13 Manejo y disposición de residuos_________Descripción: El establecimiento cuenta con el plan de gestión integral de residuos sólidos (ordinarios)//Soporte: Resolución 754 de 2014"
                              ],
    "DOTACION": ["5.1 Cuenta con la dotación y muebles exclusivos y necesarios para la adquisición, recepción, almacenamiento, conservación (como manejo de cadena de frio, medicamentos fotosensibles, higroscópicos entre otros) y dispensacion de los medicamentos y dispositivos médicos para la realización de los procesos que ofrezcan, de acuerdo con las recomendaciones dadas por los fabricantes, además de las condiciones de temperatura y humedad, registro de condiciones ambientales, termo higrómetros calibrados_________Descripción: Verifique que cuenta con estantería de material sanitario, impermeable y fácil de limpiar. (estibas plásticas, no de madera) suficiente para el almacenamiento de los medicamentos de acuerdo a su condición y cantidad //Soporte: Resolución 1403 de 2007 - Titulo 2 Capitulo 2, literal 3",
                 "5.2 Corresponde a Pregunta 5.1_________Descripción: Cuenta con equipos para la medición de condiciones de temperatura y humedad y los mismos se encuentran en funcionamiento y calibrados.//Solicite las hojas de vida y las certificados de calibración. Valide que la empresa de calibración se encuentre certificada por la ONAC.//Solicite el cronograma de mantenimiento y certificados de los equipos refrigerantes.",
                 "5.3 Corresponde a Pregunta 5.1_________Descripción: Solicite los registros de condiciones de temperatura y humedad, verifique los datos actualizados y que se encuentren en los niveles de seguridad establecidos, en caso de tener algún dato fuera del rango solicite la acción correctiva realizada para el caso.",
                 "5.4 Se evidencia equipos e implementos de seguridad en funcionamiento y ubicados donde tengan fácil acceso (extintores, barandas, estibas, extractoras)_________Descripción: Cuentan con extintores en funcionamiento, ubicados de acuerdo a las normas de seguridad, con fecha vigente de recarga y señalizada su ubicación//Soporte: Resolución 1403 de 2007 - Titulo 2 Capitulo 2, literal 3.2",
                 "5.5 Cuenta con los equipos necesarios para cumplir con el plan de contingencia, en caso de falla eléctrica para mantener la cadena de frío._________Descripción: Valide el plan de contingencia que se tiene implementado en caso de falla de temperatura y verifique que se cuente con los insumos necesarios para esta acción.//Soporte: Resolución 1403 de 2007 - Titulo 2 Capitulo 2, literal 3,2",
                 "5.6 Cuenta con medios refrigerantes para el almacenamiento de medicamentos que lo requieren_________Descripción: Verifique que las neveras sean de uso exclusivo para almacenamiento de los medicamentos que lo requieren//Soporte: Resolución 1403 de 2007 - Titulo 2 capitulo 2, literal 3 (Recepción y almacenamiento de medicamentos y dispositivos médicos)",
                 "5.7 Cuenta con literatura científica disponible y aceptada internacionalmente;  referencias bibliográficas actualizadas y confiables sobre farmacología y farmacoterapia para su consulta//Soporte: Resolución 1403 de 2007 - Titulo 1 - Capitulo 5, literal 1.2",
                 "5.8 Cuenta con Kit de manejo de derrames y ruptura de medicamentos_________Descripción: Verifique que este kit se encuentre completo para su uso.//Soporte: Resolución 3100/2019"
                 ],
    "PROCESOS PRIORITARIOS": ["6.1 Recepción_________Descripción: Solicite el documento del proceso de recepción técnica administrativa de medicamentos, indague como se realiza y valide en las actas su correcta ejecución.//Soporte: Resolución 1403 de 2007 - Titulo 2 capitulo 2, literal 3 (Recepción y almacenamiento de medicamentos y dispositivos médicos)",
                              "6.1.1 Recepción_________Descripción: En caso que transporten medicamentos y dispositivos médicos a otras sedes o sucursales, verifican las condiciones en que son transportados y llevan registro de dicho procedimiento (documento soporte de traslado)//Soporte: Resolución 1403 de 2007 - Titulo 2 capitulo 2, literal 3 (Recepción y almacenamiento de medicamentos y dispositivos médicos)",
                              "6.1.2 Recepción_________Descripción: Se realiza la identificación y marcación de medicamentos lasa y alto riesgo//Soporte: Resolución 1403 de 2007 - Titulo 2 capitulo 2, literal 3 (Recepción y almacenamiento de medicamentos y dispositivos médicos)",
                              "6.1.3 Recepción_________Descripción: Se tienen en cuenta las condiciones dadas por el fabricante para el almacenamiento de medicamentos y dispositivos médicos//Soporte: Resolución 1403 de 2007 - Titulo 2 capitulo 2, literal 3 (Recepción y almacenamiento de medicamentos y dispositivos médicos)",
                              "6.1.4 Recepción_________Descripción: Verificar el procedimiento de recepción de medicamentos y dispositivos médicos que llegan del CEDI a las droguerías, verificando mantenimiento de la cadena de frio y condiciones de embalaje.//Soporte: Resolución 1403 de 2007 - Titulo 2 capitulo 2, literal 3 (Recepción y almacenamiento de medicamentos y dispositivos médicos)",
                              "6.2 Almacenamiento_________Descripción: Solicite el documento del proceso de almacenamiento y valide que se realice en la manera descrita, tener en cuenta que debe ser acuerdo a un método de clasificación (alfabéticamente, forma farmacéutica, otros) y los dispositivos médicos deben almacenarse de acuerdo a lo establecido, siempre y cuando garantice el orden y minimice eventos de confusión.//Soporte: Resolución 1403 de 2007 - Titulo 2 capitulo 2, literal 3 (Recepción y almacenamiento de medicamentos y dispositivos médicos)",
                              "6.2.1 Almacenamiento_________Descripción: El establecimiento está libre de productos farmacéuticos prohibidos (medicamentos de control especial sin autorización, vencidos en el área de dispensación, muestras médicas, productos con enmendaduras o etiquetas que oculten información, sin registro sanitario, con el sistema de seguridad alterado, entre otros).//Soporte: Art 77, Dec 677/95. Art 45, Dec 3554/04.",
                              "6.2.2 Almacenamiento_________Descripción: Solicite el proceso de control de fechas de vencimiento de medicamentos y valide que se lleve a cabo y que los auxiliares lo conozcan. Adicionalmente valide que no haya medicamentos vencidos ubicados en las estanterías de suministro.//Soporte: Resolución 1403 de 2007 - Titulo 2 capitulo 2, literal 3 (Recepción y almacenamiento de medicamentos y dispositivos médicos)",
                              "6.3 Medicamentos de control especial_________Descripción: Verifique que el área para el almacenamiento de los medicamentos de control especial sea independiente, diferenciada, señalizada y se encuentra bajo llave en área de acceso restringido al público general. Solo el director técnico debe tener acceso, debe solicitarse el soporte que delega la responsabilidad a los auxiliares para cuando no esté el director técnico y debe especificar nombre y cedula del responsable.//Soporte: Resolución 1478 de 2006",
                              "6.3.1 Medicamentos de control especial_________Descripción: Cumple con la presentación de informe al FNE dentro de las fechas establecidas. (Validar en ciudades fuera de Bogotá y Cundinamarca estas se validarán a nivel central)//Soporte: Resolución 1478 de 2006",
                              "6.3.2 Medicamentos de control especial_________Descripción: Tome al menos 10 medicamentos aleatoriamente y valide las existencias Vs documento de control de dispensación (libro). Debe coincidir la existencia física Vs lo reportado en el libro.//Soporte: Resolución 1478 de 2006",
                              "6.4 Dispensación_________Descripción: Solicite el documento con el proceso de dispensación de medicamentos y dispositivos médicos y otros productos farmacéuticos, valide que se esté ejecutando de acuerdo a lo descrito.//Soporte: Resolución 1403 de 2007 - Titulo 2 capitulo 2, literal 5 (Dispensación de medicamentos)",
                              "6.4.1 Dispensación_________Descripción: Valide que se esté colocando el sello de dispensado en los medicamentos de control especial",
                              "6.4.2 Dispensación_________Descripción: Verifique aleatoriamente si al paciente no se le realiza entrega completa de la orden medica por algún medicamento que no cuenta con novedad en inventario, que a este se le genere el pendiente en sistema y se le ofrezca el envío a domicilio del mismo. Llevar consigo la última versión del informe de novedades.//Soporte: Resolución 1403 de 2007 - Titulo 2 capitulo 2, literal 5 (Dispensación de medicamentos); resolución 1604/2013",
                              "6.5 Atención farmacéutica_________Descripción: Validar que la asesoría farmacológica no se este dando por parte de personal  diferente al químico farmacéutico //Soporte: Resolución 1403 de 2007 - Titulo 2 - Capitulo 3; resolucion 1604/2013",
                              "6.6 Errores de medicación, Farmacovigilancia y Tecnovigilancia_________Descripción: Los funcionarios de la droguería conoce los programas de farmacovigilancia, tecnovigilancia institucionales y errores de medicación.//Soporte: Resolución 1403 de 2007 - Titulo 2 - Capitulo 3 Resolución 2004009455 de 2006 Decreto 2200 de 2005 Resolución 4826 de 2008",
                              "6.7 Alertas sanitarias_________Descripción: Verifique si se realiza la socialización de las alertas Sanitarias al personal de la farmación emitidas por los entes regulatorios."
                              ],
    "GESTION DE LA CALIDAD": ["7.1 Cuenta con visitas de entes de control con algún tipo de hallazgos y los mismos ya se encuentran solventados_________Descripción: Valide con soporte físico la útlima visita de entes de control y verifique si hay requerimientos y los mismos ya se encuentran solventados//Soporte: Resolución 1403 - Titulo 1 - Capitulo 4",
                             "7.2 Realizan inventario (periódico, trimestral o semestral)_________Descripción: Solicite el inventario con su última actualización.//Soporte: Resolución 1403 - Titulo 1 - Capitulo 4",
                             "7.3 Evaluación y seguimiento a la dispensación_________Descripción: La institución cuenta con actividades de seguimiento a la adherencia del procedimiento de dispensación de medicamentos a los auxiliares de farmacia. (Metodo observacional)//Soporte: Modelo operativo dispensación de medicamentos",
                             "7.4 Establecimiento cuenta con matriz de riesgo y la misma es de conocimiento por parte de los funcionarios_________Descripción: Solicitar la matriz de riesgo y validar que los funcionarios la conozcan.//Soporte: Resolución 1403 - Titulo 1 - Capitulo 4"
                             ],
    "APLICATIVOS TÉCNOLOGICOS (SISTEMA)": ["8.1 Cuenta con medios, preferiblemente computarizados que permitan el registro de adecuado de formulas prescritas, medicamentos de control especial y demas productos que lo requieran_________Descripción: Verificar el sistema que manejan en el punto, su correcto funcionamiento y utilización.//Soporte: Resolución 1403 de 2007 - Titulo 1 - Capitulo 5, literal 1.2",
                                           "8.2 Corresponde a pregunta anterior_________Descripción: Validar de manera aleatoria en el informe de novedades que los medicamentos que presentan novedad (desabastecidos) se encuentran bloqueados en el aplicativo de dispensación CYGNUS.Validar para los casos en los que no cuenta con disponibilidad en el punto la generación del pendiente en el sistema CYGNUS."
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
            "respuesta": "Cumple totalmente",
            "valor": 100
        }

    # Mostrar la pregunta y permitir selección
    respuesta = st.radio(
        pregunta,
        ["Cumple totalmente", "Cumple parcialmente", "Incumple totalmente"],
        key=f"{grupo_actual}_{pregunta}",
        index=["Cumple totalmente", "Cumple parcialmente", "Incumple totalmente"].index(st.session_state["responses"][grupo_actual][pregunta]["respuesta"])
    )

    # Guardar respuesta y valor
    valor = 100 if respuesta == "Cumple totalmente" else 50 if respuesta == "Cumple parcialmente" else 0
    st.session_state["responses"][grupo_actual][pregunta] = {"respuesta": respuesta, "valor": valor}

# Calcular promedio
total_valores = sum(
    r["valor"] for g in st.session_state["responses"].values() for r in g.values()
)
num_preguntas = len(preguntas) * len(grupos)
promedio = total_valores / num_preguntas if num_preguntas > 0 else 0

st.sidebar.metric("Promedio Total", promedio)

# Botones
st.sidebar.button("Finalizar y Enviar", on_click=finalizar_formulario)
st.sidebar.button("Nuevo formulario", on_click=reiniciar_formulario)
st.sidebar.button("Guardar", on_click=guardar_estado)

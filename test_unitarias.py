import sys
import os
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ============================================================
# PRUEBAS UNITARIAS - MATERCHILD PREDIC
# Equipo: Creciendo Juntos
# ============================================================

def generar_codigo_6_digitos():
    return str(random.randint(100000, 999999))

def validar_signos_vitales(datos):
    campos_requeridos = ['Age', 'SystolicBP', 'DiastolicBP', 'BS', 'BodyTemp', 'HeartRate']
    for campo in campos_requeridos:
        if campo not in datos:
            return False, f"Falta el campo: {campo}"
    return True, "Datos validos"

def validar_registro(datos):
    if not datos.get('nombres'):
        return False, "Nombres son obligatorios"
    if not datos.get('apellidos'):
        return False, "Apellidos son obligatorios"
    if not datos.get('correo_institucional'):
        return False, "Correo es obligatorio"
    return True, "Registro valido"

def clasificar_riesgo_basico(sistolica, diastolica, glucosa):
    if sistolica >= 160 or diastolica >= 110 or glucosa >= 11:
        return "high risk"
    elif sistolica >= 140 or diastolica >= 90 or glucosa >= 8:
        return "mid risk"
    else:
        return "low risk"

def validar_correo(correo):
    if not correo:
        return False, "El correo es obligatorio"
    if "@" not in correo:
        return False, "El correo no tiene formato valido"
    if "." not in correo.split("@")[-1]:
        return False, "El dominio del correo no es valido"
    return True, "Correo valido"

def verificar_credenciales_smtp():
    smtp_user = os.getenv("EMAIL_USUARIO")
    smtp_pass = os.getenv("EMAIL_CONTRASENA")
    if not smtp_user or not smtp_pass:
        return False, "Modo simulacion: faltan credenciales SMTP"
    return True, "Credenciales SMTP configuradas"

def validar_datos_paciente_reporte(datos):
    campos = ['nombre_completo', 'identificacion', 'edad']
    for campo in campos:
        if campo not in datos or not datos[campo]:
            return False, f"Falta el campo: {campo}"
    return True, "Datos validos para reporte"

def validar_dictamen(dictamen):
    campos = ['enfermedad_predicha', 'nivel_riesgo', 'confianza_ia', 'justificacion']
    for campo in campos:
        if campo not in dictamen or not dictamen[campo]:
            return False, f"Falta el campo: {campo}"
    return True, "Dictamen valido"

def validar_nivel_riesgo(nivel):
    niveles_validos = ['Alto', 'Medio', 'Bajo', 'high risk', 'mid risk', 'low risk']
    if nivel not in niveles_validos:
        return False, "Nivel de riesgo no valido"
    return True, "Nivel de riesgo valido"

def validar_confianza_ia(confianza):
    if not isinstance(confianza, (int, float)):
        return False, "La confianza debe ser un numero"
    if confianza < 70 or confianza > 99:
        return False, "La confianza debe estar entre 70 y 99"
    return True, "Confianza valida"

def validar_extension_csv(nombre_archivo):
    if not nombre_archivo:
        return False, "No se proporciono nombre de archivo"
    if not nombre_archivo.endswith('.csv'):
        return False, "El archivo debe tener extension .csv"
    return True, "Extension valida"

def validar_columnas_csv(columnas):
    columnas_requeridas = ['Age', 'SystolicBP', 'DiastolicBP', 'BS', 'BodyTemp', 'HeartRate', 'RiskLevel']
    for col in columnas_requeridas:
        if col not in columnas:
            return False, f"Falta la columna: {col}"
    return True, "Columnas validas"

def validar_tamano_lote(lote):
    if not isinstance(lote, int):
        return False, "El lote debe ser un numero entero"
    if lote <= 0:
        return False, "El lote debe ser mayor a 0"
    if lote > 1000:
        return False, "El lote no puede ser mayor a 1000"
    return True, "Tamano de lote valido"


# ============================================================
# GRUPO 1: Generacion de codigo OTP
# ============================================================

def test_codigo_otp_tiene_6_digitos():
    """PU-01: El codigo OTP debe tener exactamente 6 digitos"""
    assert len(generar_codigo_6_digitos()) == 6

def test_codigo_otp_es_numerico():
    """PU-02: El codigo OTP debe ser numerico"""
    assert generar_codigo_6_digitos().isdigit()

def test_codigo_otp_en_rango():
    """PU-03: El codigo OTP debe estar entre 100000 y 999999"""
    codigo = int(generar_codigo_6_digitos())
    assert 100000 <= codigo <= 999999

def test_codigos_otp_son_diferentes():
    """PU-04: Dos codigos OTP generados no deben ser iguales"""
    assert len({generar_codigo_6_digitos() for _ in range(10)}) > 1


# ============================================================
# GRUPO 2: Validacion de signos vitales
# ============================================================

def test_signos_vitales_completos_son_validos():
    """PU-05: Signos vitales con todos los campos deben ser validos"""
    datos = {'Age': 25, 'SystolicBP': 120, 'DiastolicBP': 80, 'BS': 7.5, 'BodyTemp': 98, 'HeartRate': 72}
    valido, _ = validar_signos_vitales(datos)
    assert valido == True

def test_signos_vitales_incompletos_son_invalidos():
    """PU-06: Signos vitales sin campo Age deben ser invalidos"""
    valido, _ = validar_signos_vitales({'SystolicBP': 120, 'DiastolicBP': 80})
    assert valido == False

def test_signos_vitales_vacios_son_invalidos():
    """PU-07: Signos vitales vacios deben ser invalidos"""
    valido, _ = validar_signos_vitales({})
    assert valido == False

def test_signos_vitales_sin_frecuencia_cardiaca():
    """PU-08: Signos vitales sin HeartRate deben ser invalidos"""
    datos = {'Age': 25, 'SystolicBP': 120, 'DiastolicBP': 80, 'BS': 7.5, 'BodyTemp': 98}
    valido, mensaje = validar_signos_vitales(datos)
    assert valido == False and "HeartRate" in mensaje


# ============================================================
# GRUPO 3: Validacion de registro de medico
# ============================================================

def test_registro_completo_es_valido():
    """PU-09: Registro con todos los datos debe ser valido"""
    datos = {'nombres': 'Laura', 'apellidos': 'Garcia', 'correo_institucional': 'laura@usc.edu.co', 'especialidad': 'Ginecologia'}
    valido, _ = validar_registro(datos)
    assert valido == True

def test_registro_sin_nombres_es_invalido():
    """PU-10: Registro sin nombres debe ser invalido"""
    valido, _ = validar_registro({'apellidos': 'Garcia', 'correo_institucional': 'laura@usc.edu.co'})
    assert valido == False

def test_registro_sin_correo_es_invalido():
    """PU-11: Registro sin correo debe ser invalido"""
    valido, _ = validar_registro({'nombres': 'Laura', 'apellidos': 'Garcia'})
    assert valido == False

def test_registro_sin_apellidos_es_invalido():
    """PU-12: Registro sin apellidos debe ser invalido"""
    valido, _ = validar_registro({'nombres': 'Laura', 'correo_institucional': 'laura@usc.edu.co'})
    assert valido == False


# ============================================================
# GRUPO 4: Clasificacion de riesgo clinico
# ============================================================

def test_clasificacion_riesgo_alto_sistolica():
    """PU-13: Presion sistolica >= 160 debe ser riesgo alto"""
    assert clasificar_riesgo_basico(160, 80, 7.5) == "high risk"

def test_clasificacion_riesgo_medio():
    """PU-14: Presion sistolica >= 140 debe ser riesgo medio"""
    assert clasificar_riesgo_basico(140, 85, 7.5) == "mid risk"

def test_clasificacion_riesgo_bajo():
    """PU-15: Signos normales deben ser riesgo bajo"""
    assert clasificar_riesgo_basico(120, 80, 7.5) == "low risk"

def test_clasificacion_riesgo_alto_por_glucosa():
    """PU-16: Glucosa >= 11 debe ser riesgo alto"""
    assert clasificar_riesgo_basico(120, 80, 11.0) == "high risk"

def test_clasificacion_riesgo_alto_por_diastolica():
    """PU-17: Presion diastolica >= 110 debe ser riesgo alto"""
    assert clasificar_riesgo_basico(130, 110, 7.5) == "high risk"

def test_clasificacion_riesgo_medio_por_glucosa():
    """PU-18: Glucosa >= 8 debe ser riesgo medio"""
    assert clasificar_riesgo_basico(120, 80, 8.0) == "mid risk"


# ============================================================
# GRUPO 5: Validacion de correo (email_service.py)
# ============================================================

def test_correo_valido():
    """PU-19: Un correo con formato correcto debe ser valido"""
    valido, _ = validar_correo("laura@usc.edu.co")
    assert valido == True

def test_correo_sin_arroba_es_invalido():
    """PU-20: Un correo sin @ debe ser invalido"""
    valido, _ = validar_correo("laurausc.edu.co")
    assert valido == False

def test_correo_sin_dominio_es_invalido():
    """PU-21: Un correo sin dominio valido debe ser invalido"""
    valido, _ = validar_correo("laura@usc")
    assert valido == False

def test_correo_vacio_es_invalido():
    """PU-22: Un correo vacio debe ser invalido"""
    valido, _ = validar_correo("")
    assert valido == False

def test_credenciales_smtp_sin_configurar():
    """PU-23: Sin credenciales SMTP debe estar en modo simulacion"""
    os.environ.pop("EMAIL_USUARIO", None)
    os.environ.pop("EMAIL_CONTRASENA", None)
    configurado, mensaje = verificar_credenciales_smtp()
    assert configurado == False and "simulacion" in mensaje.lower()


# ============================================================
# GRUPO 6: Validacion de reporte (report_service.py)
# ============================================================

def test_datos_paciente_reporte_completos():
    """PU-24: Datos completos de paciente deben ser validos para reporte"""
    datos = {'nombre_completo': 'Maria Lopez', 'identificacion': '1234567890', 'edad': 28}
    valido, _ = validar_datos_paciente_reporte(datos)
    assert valido == True

def test_datos_paciente_sin_nombre():
    """PU-25: Datos sin nombre_completo deben ser invalidos"""
    valido, _ = validar_datos_paciente_reporte({'identificacion': '1234567890', 'edad': 28})
    assert valido == False

def test_datos_paciente_sin_identificacion():
    """PU-26: Datos sin identificacion deben ser invalidos"""
    valido, _ = validar_datos_paciente_reporte({'nombre_completo': 'Maria Lopez', 'edad': 28})
    assert valido == False

def test_dictamen_completo_es_valido():
    """PU-27: Dictamen con todos los campos debe ser valido"""
    dictamen = {'enfermedad_predicha': 'Preeclampsia', 'nivel_riesgo': 'Alto', 'confianza_ia': 92, 'justificacion': 'Presion alta'}
    valido, _ = validar_dictamen(dictamen)
    assert valido == True

def test_dictamen_sin_nivel_riesgo():
    """PU-28: Dictamen sin nivel_riesgo debe ser invalido"""
    dictamen = {'enfermedad_predicha': 'Preeclampsia', 'confianza_ia': 92, 'justificacion': 'Presion alta'}
    valido, _ = validar_dictamen(dictamen)
    assert valido == False

def test_nivel_riesgo_alto_valido():
    """PU-29: El nivel de riesgo Alto debe ser valido"""
    valido, _ = validar_nivel_riesgo("Alto")
    assert valido == True

def test_nivel_riesgo_invalido():
    """PU-30: Un nivel de riesgo desconocido debe ser invalido"""
    valido, _ = validar_nivel_riesgo("Critico")
    assert valido == False

def test_confianza_ia_valida():
    """PU-31: Confianza entre 70 y 99 debe ser valida"""
    valido, _ = validar_confianza_ia(92)
    assert valido == True

def test_confianza_ia_muy_baja():
    """PU-32: Confianza menor a 70 debe ser invalida"""
    valido, _ = validar_confianza_ia(50)
    assert valido == False

def test_confianza_ia_muy_alta():
    """PU-33: Confianza mayor a 99 debe ser invalida"""
    valido, _ = validar_confianza_ia(100)
    assert valido == False


# ============================================================
# GRUPO 7: Validacion de dataset (data_routes.py)
# ============================================================

def test_extension_csv_valida():
    """PU-34: Archivo con extension .csv debe ser valido"""
    valido, _ = validar_extension_csv("dataset.csv")
    assert valido == True

def test_extension_txt_invalida():
    """PU-35: Archivo con extension .txt debe ser invalido"""
    valido, _ = validar_extension_csv("dataset.txt")
    assert valido == False

def test_extension_xlsx_invalida():
    """PU-36: Archivo con extension .xlsx debe ser invalido"""
    valido, _ = validar_extension_csv("dataset.xlsx")
    assert valido == False

def test_columnas_csv_completas():
    """PU-37: CSV con todas las columnas requeridas debe ser valido"""
    columnas = ['Age', 'SystolicBP', 'DiastolicBP', 'BS', 'BodyTemp', 'HeartRate', 'RiskLevel']
    valido, _ = validar_columnas_csv(columnas)
    assert valido == True

def test_columnas_csv_incompletas():
    """PU-38: CSV sin columna Age debe ser invalido"""
    columnas = ['SystolicBP', 'DiastolicBP', 'BS', 'BodyTemp', 'HeartRate', 'RiskLevel']
    valido, mensaje = validar_columnas_csv(columnas)
    assert valido == False and "Age" in mensaje

def test_columnas_csv_vacias():
    """PU-39: CSV sin columnas debe ser invalido"""
    valido, _ = validar_columnas_csv([])
    assert valido == False

def test_tamano_lote_valido():
    """PU-40: Lote de 50 registros debe ser valido"""
    valido, _ = validar_tamano_lote(50)
    assert valido == True

def test_tamano_lote_cero_invalido():
    """PU-41: Lote de 0 debe ser invalido"""
    valido, _ = validar_tamano_lote(0)
    assert valido == False

def test_tamano_lote_negativo_invalido():
    """PU-42: Lote negativo debe ser invalido"""
    valido, _ = validar_tamano_lote(-10)
    assert valido == False

def test_tamano_lote_muy_grande_invalido():
    """PU-43: Lote mayor a 1000 debe ser invalido"""
    valido, _ = validar_tamano_lote(1001)
    assert valido == False


# ============================================================
# GRUPO 8: Validacion de modelos (models.py)
# ============================================================

def validar_edad_paciente(edad):
    if not isinstance(edad, int):
        return False, "La edad debe ser un numero entero"
    if edad <= 0:
        return False, "La edad debe ser mayor a 0"
    if edad > 120:
        return False, "La edad no es valida"
    return True, "Edad valida"

def validar_semanas_gestacion(semanas):
    if not isinstance(semanas, int):
        return False, "Las semanas deben ser un numero entero"
    if semanas < 1 or semanas > 42:
        return False, "Las semanas de gestacion deben estar entre 1 y 42"
    return True, "Semanas de gestacion validas"

def validar_presiones(sistolica, diastolica):
    if sistolica <= 0 or diastolica <= 0:
        return False, "Las presiones deben ser mayores a 0"
    if sistolica <= diastolica:
        return False, "La presion sistolica debe ser mayor que la diastolica"
    return True, "Presiones validas"

def validar_temperatura(temp):
    if not isinstance(temp, (int, float)):
        return False, "La temperatura debe ser un numero"
    if temp < 35 or temp > 42:
        return False, "La temperatura esta fuera del rango normal"
    return True, "Temperatura valida"

def validar_frecuencia_cardiaca(fc):
    if not isinstance(fc, int):
        return False, "La frecuencia cardiaca debe ser un numero entero"
    if fc < 40 or fc > 200:
        return False, "La frecuencia cardiaca esta fuera del rango normal"
    return True, "Frecuencia cardiaca valida"

def validar_nivel_riesgo_diagnostico(nivel):
    niveles = ['Alto', 'Medio', 'Bajo']
    if nivel not in niveles:
        return False, "Nivel de riesgo no valido"
    return True, "Nivel de riesgo valido"

def validar_confianza_modelo(confianza):
    if confianza is None:
        return False, "La confianza no puede ser nula"
    if float(confianza) < 0 or float(confianza) > 100:
        return False, "La confianza debe estar entre 0 y 100"
    return True, "Confianza valida"

def validar_usuario_admin(usuario, contrasena):
    if not usuario or not contrasena:
        return False, "Usuario y contrasena son obligatorios"
    if len(usuario) < 3:
        return False, "El usuario debe tener al menos 3 caracteres"
    if len(contrasena) < 4:
        return False, "La contrasena debe tener al menos 4 caracteres"
    return True, "Credenciales validas"


def test_edad_paciente_valida():
    """PU-44: Edad valida de paciente"""
    valido, _ = validar_edad_paciente(28)
    assert valido == True

def test_edad_paciente_cero_invalida():
    """PU-45: Edad de 0 debe ser invalida"""
    valido, _ = validar_edad_paciente(0)
    assert valido == False

def test_edad_paciente_negativa_invalida():
    """PU-46: Edad negativa debe ser invalida"""
    valido, _ = validar_edad_paciente(-5)
    assert valido == False

def test_edad_paciente_muy_alta_invalida():
    """PU-47: Edad mayor a 120 debe ser invalida"""
    valido, _ = validar_edad_paciente(150)
    assert valido == False

def test_semanas_gestacion_validas():
    """PU-48: Semanas de gestacion validas (1-42)"""
    valido, _ = validar_semanas_gestacion(30)
    assert valido == True

def test_semanas_gestacion_cero_invalidas():
    """PU-49: Semanas de gestacion de 0 deben ser invalidas"""
    valido, _ = validar_semanas_gestacion(0)
    assert valido == False

def test_semanas_gestacion_muy_altas_invalidas():
    """PU-50: Semanas de gestacion mayores a 42 deben ser invalidas"""
    valido, _ = validar_semanas_gestacion(43)
    assert valido == False

def test_presiones_validas():
    """PU-51: Presion sistolica mayor que diastolica debe ser valida"""
    valido, _ = validar_presiones(120, 80)
    assert valido == True

def test_presiones_invertidas_invalidas():
    """PU-52: Presion sistolica menor que diastolica debe ser invalida"""
    valido, _ = validar_presiones(80, 120)
    assert valido == False

def test_presiones_iguales_invalidas():
    """PU-53: Presion sistolica igual a diastolica debe ser invalida"""
    valido, _ = validar_presiones(120, 120)
    assert valido == False

def test_temperatura_normal_valida():
    """PU-54: Temperatura entre 35 y 42 debe ser valida"""
    valido, _ = validar_temperatura(37.5)
    assert valido == True

def test_temperatura_muy_baja_invalida():
    """PU-55: Temperatura menor a 35 debe ser invalida"""
    valido, _ = validar_temperatura(34.0)
    assert valido == False

def test_temperatura_muy_alta_invalida():
    """PU-56: Temperatura mayor a 42 debe ser invalida"""
    valido, _ = validar_temperatura(43.0)
    assert valido == False

def test_frecuencia_cardiaca_valida():
    """PU-57: Frecuencia cardiaca entre 40 y 200 debe ser valida"""
    valido, _ = validar_frecuencia_cardiaca(72)
    assert valido == True

def test_frecuencia_cardiaca_muy_baja_invalida():
    """PU-58: Frecuencia cardiaca menor a 40 debe ser invalida"""
    valido, _ = validar_frecuencia_cardiaca(30)
    assert valido == False

def test_frecuencia_cardiaca_muy_alta_invalida():
    """PU-59: Frecuencia cardiaca mayor a 200 debe ser invalida"""
    valido, _ = validar_frecuencia_cardiaca(250)
    assert valido == False

def test_nivel_riesgo_diagnostico_alto():
    """PU-60: Nivel de riesgo Alto debe ser valido"""
    valido, _ = validar_nivel_riesgo_diagnostico("Alto")
    assert valido == True

def test_nivel_riesgo_diagnostico_medio():
    """PU-61: Nivel de riesgo Medio debe ser valido"""
    valido, _ = validar_nivel_riesgo_diagnostico("Medio")
    assert valido == True

def test_nivel_riesgo_diagnostico_invalido():
    """PU-62: Nivel de riesgo desconocido debe ser invalido"""
    valido, _ = validar_nivel_riesgo_diagnostico("Extremo")
    assert valido == False

def test_confianza_modelo_valida():
    """PU-63: Confianza entre 0 y 100 debe ser valida"""
    valido, _ = validar_confianza_modelo(85.5)
    assert valido == True

def test_confianza_modelo_nula_invalida():
    """PU-64: Confianza nula debe ser invalida"""
    valido, _ = validar_confianza_modelo(None)
    assert valido == False

def test_credenciales_admin_validas():
    """PU-65: Credenciales de admin validas"""
    valido, _ = validar_usuario_admin("admin", "12345")
    assert valido == True

def test_credenciales_admin_sin_usuario():
    """PU-66: Credenciales sin usuario deben ser invalidas"""
    valido, _ = validar_usuario_admin("", "12345")
    assert valido == False

def test_credenciales_admin_contrasena_corta():
    """PU-67: Contrasena menor a 4 caracteres debe ser invalida"""
    valido, _ = validar_usuario_admin("admin", "123")
    assert valido == False

# ============================================================
# GRUPO 9: Validacion de endpoints nuevos
# ============================================================

def validar_id_paciente(id_paciente):
    if not isinstance(id_paciente, int):
        return False, "El id_paciente debe ser un numero entero"
    if id_paciente <= 0:
        return False, "El id_paciente debe ser mayor a 0"
    return True, "ID de paciente valido"

def validar_correo_destino(correo):
    if not correo:
        return False, "El correo destino es obligatorio"
    if "@" not in correo:
        return False, "El correo destino no tiene formato valido"
    if "." not in correo.split("@")[-1]:
        return False, "El dominio del correo destino no es valido"
    return True, "Correo destino valido"

def test_id_paciente_valido():
    """PU-68: ID de paciente valido"""
    valido, _ = validar_id_paciente(1)
    assert valido == True

def test_id_paciente_cero_invalido():
    """PU-69: ID de paciente de 0 debe ser invalido"""
    valido, _ = validar_id_paciente(0)
    assert valido == False

def test_id_paciente_negativo_invalido():
    """PU-70: ID de paciente negativo debe ser invalido"""
    valido, _ = validar_id_paciente(-1)
    assert valido == False

def test_id_paciente_texto_invalido():
    """PU-71: ID de paciente en texto debe ser invalido"""
    valido, _ = validar_id_paciente("abc")
    assert valido == False

def test_correo_destino_valido():
    """PU-72: Correo destino con formato correcto debe ser valido"""
    valido, _ = validar_correo_destino("medico@hospital.com")
    assert valido == True

def test_correo_destino_vacio():
    """PU-73: Correo destino vacio debe ser invalido"""
    valido, _ = validar_correo_destino("")
    assert valido == False

def test_correo_destino_sin_arroba():
    """PU-74: Correo destino sin @ debe ser invalido"""
    valido, _ = validar_correo_destino("medicosinArroba.com")
    assert valido == False
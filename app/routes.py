from flask import Blueprint, request, jsonify
from sqlalchemy import or_
from app.models import db, Usuario, SesionOTP, Administrador, PacienteSintetica, ControlPrenatal, ReglaClasificacion, DiagnosticoRiesgo
from app.services.email_service import enviar_correo_otp
import random
from datetime import datetime, timedelta, timezone
from app.services.ai_service import AIService

auth_bp = Blueprint('auth', __name__)

def generar_codigo_6_digitos():
    return str(random.randint(100000, 999999))

@auth_bp.route('/api/auth/register', methods=['POST'])
def registrar_usuario():
    datos = request.get_json()
    
    # Capturamos los datos del frontend
    nombres = datos.get('nombres')
    apellidos = datos.get('apellidos')
    correo = datos.get('correo_institucional')
    especialidad = datos.get('especialidad')

    if not correo or not nombres or not apellidos:
        return jsonify({'error': 'Nombres, apellidos y correo son obligatorios'}), 400

    if Usuario.query.filter_by(correo_institucional=correo).first():
        return jsonify({'error': 'El correo ya está registrado'}), 400

    # Guardamos usando los campos exactos de tu modelo
    nuevo_usuario = Usuario(
        nombres=nombres,
        apellidos=apellidos,
        correo_institucional=correo,
        especialidad=especialidad
    )
    
    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({'mensaje': 'Médico registrado exitosamente, Inicie sesión'}), 201

@auth_bp.route('/api/auth/solicitar-otp', methods=['POST'])
def solicitar_otp():
    datos = request.get_json()
    correo = datos.get('correo')
    
    if not correo:
        return jsonify({'error': 'El correo es obligatorio'}), 400

    # 1. Buscar estrictamente al usuario (Médico ya debe estar registrado)
    usuario = Usuario.query.filter_by(correo_institucional=correo).first()
    
    # Si intentan loguearse sin haberse registrado primero, les arrojamos error
    if not usuario:
        return jsonify({'error': 'El correo institucional no se encuentra registrado.'}), 404

    # 2. Generar código y tiempo de expiración (10 min)
    codigo = generar_codigo_6_digitos()
    expiracion = datetime.now(timezone.utc) + timedelta(minutes=10)

    # 3. Guardar en la base de datos
    # Primero invalidamos códigos anteriores no usados
    SesionOTP.query.filter_by(id_usuario=usuario.id_usuario, usado=False).update({'usado': True})
    
    nueva_sesion = SesionOTP(
        id_usuario=usuario.id_usuario,
        codigo_otp=codigo,
        fecha_expiracion=expiracion
    )
    db.session.add(nueva_sesion)
    db.session.commit()

    # 4. Enviar el correo REAL usando tu cuenta de Outlook
    # Modificado para pasarle tus variables exactas: 'correo' y 'codigo'
    if enviar_correo_otp(correo, codigo):
        return jsonify({'mensaje': 'Código enviado exitosamente', 'correo': correo}), 200
    else:
        return jsonify({'error': 'El servidor SMTP falló al despachar el correo electrónico.'}), 500
    
@auth_bp.route('/api/auth/verificar-otp', methods=['POST'])
def verificar_otp():
    datos = request.get_json()
    correo = datos.get('correo')
    codigo_ingresado = datos.get('codigo_otp')

    if not correo or not codigo_ingresado:
        return jsonify({'error': 'Faltan datos obligatorios'}), 400

    # 1. Buscamos al usuario
    usuario = Usuario.query.filter_by(correo_institucional=correo).first()
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    # 2. Buscamos el código OTP más reciente que no se haya usado
    sesion = SesionOTP.query.filter_by(
        id_usuario=usuario.id_usuario, 
        usado=False
    ).order_by(SesionOTP.id_sesion.desc()).first()

    if not sesion:
        return jsonify({'error': 'No hay un código pendiente o ya fue usado'}), 400

    # 3. Verificamos si superó el límite de intentos (Máximo 3)
    if sesion.intentos_fallidos >= 3:
        sesion.usado = True
        db.session.commit()
        return jsonify({'error': 'Demasiados intentos. Solicite un nuevo código.'}), 403

    # 4. Verificamos si el código ya expiró (pasaron los 10 min)
    if datetime.now(timezone.utc) > sesion.fecha_expiracion:
        sesion.usado = True
        db.session.commit()
        return jsonify({'error': 'El código ha expirado. Solicite uno nuevo.'}), 400

    # 5. Verificamos si el código es correcto
    if sesion.codigo_otp != str(codigo_ingresado):
        sesion.intentos_fallidos += 1
        db.session.commit()
        return jsonify({'error': 'Código incorrecto. Intente de nuevo.'}), 401

    # 6. Si TODO es correcto: Marcamos como usado y actualizamos último acceso
    sesion.usado = True
    usuario.ultimo_acceso = datetime.now(timezone.utc)
    db.session.commit()

    # 7.Buscamos al usuario por su correo institucional
    usuario = Usuario.query.filter_by(correo_institucional=correo).first()

    return jsonify({
        'mensaje': 'Autenticación exitosa',
        'usuario': {
            'nombre_completo': f"Dr. {usuario.nombres} {usuario.apellidos}",
            'especialidad': usuario.especialidad
        }
    }), 200

@auth_bp.route('/api/auth/admin-login', methods=['POST'])
def admin_login():
    datos = request.get_json()
    usuario_ingresado = datos.get('usuario')
    contrasena_ingresada = datos.get('contrasena')

    if not usuario_ingresado or not contrasena_ingresada:
        return jsonify({'error': 'Usuario y contraseña obligatorios'}), 400

    # Buscamos el administrador en la base de datos
    admin = Administrador.query.filter_by(usuario=usuario_ingresado).first()

    if not admin or admin.contrasena != str(contrasena_ingresada):
        return jsonify({'error': 'Credenciales de administrador incorrectas'}), 401

    return jsonify({
        'mensaje': 'Ingreso de administrador exitoso',
        'admin': {
            'usuario': admin.usuario,
            'nombre': admin.nombre_completo
        }
    }), 200
    
@auth_bp.route('/api/pacientes', methods=['GET'])
def obtener_pacientes_recientes():
    # 1. Capturamos lo que el usuario escribió
    busqueda = request.args.get('q')
    
    # 2. Inicializamos la variable vacía por seguridad
    pacientes_db = []
    
    if busqueda:
        # Si hay texto, buscamos en los nombres, apellidos o identificación
        termino = f"%{busqueda}%"
        pacientes_db = PacienteSintetica.query.filter(
            or_(
                PacienteSintetica.nombres_ficticios.ilike(termino),
                PacienteSintetica.apellidos_ficticios.ilike(termino),
                PacienteSintetica.identificacion_ficticia.ilike(termino)
            )
        ).all()
    else:
        # Si está vacío, traemos los 5 más recientes
        pacientes_db = PacienteSintetica.query.order_by(PacienteSintetica.id_paciente.desc()).limit(5).all()
    
    # 3. Formateamos y enviamos la respuesta
    resultado = []
    for p in pacientes_db:
        control = ControlPrenatal.query.filter_by(id_paciente=p.id_paciente).first()
        
        if control:
            resultado.append({
                'id_paciente': p.id_paciente,
                'cedula': p.identificacion_ficticia,
                'nombres_completos': f"{p.nombres_ficticios} {p.apellidos_ficticios}",
                'edad': p.edad,
                'signos_vitales': {
                    'presion': f"{control.presion_sistolica}/{control.presion_diastolica}",
                    'glucosa': control.bs_azucar_sangre,
                    'temperatura': control.temperatura_corporal,
                    'ritmo_cardiaco': control.frecuencia_cardiaca
                }
            })
            
    return jsonify(resultado), 200

@auth_bp.route('/api/pacientes/<int:id_paciente>', methods=['GET'])
def obtener_paciente_por_id(id_paciente):
    # Buscamos al paciente por su ID
    paciente = PacienteSintetica.query.get(id_paciente)
    
    if not paciente:
        return jsonify({'error': 'Paciente no encontrado'}), 404
        
    # CORRECCIÓN: Buscamos el control prenatal sin exigir la columna de fecha
    control = ControlPrenatal.query.filter_by(id_paciente=id_paciente).first()
    
    # Armamos el paquete de datos
    datos_paciente = {
        'id_paciente': paciente.id_paciente,
        'cedula': paciente.identificacion_ficticia,
        'edad': paciente.edad,
        'peso': control.peso if control else 0,
        'semanas_gestacion': control.semanas_gestacion if control else 0,
        'signos_vitales': {
            'presion_sistolica': control.presion_sistolica if control else 0,
            'presion_diastolica': control.presion_diastolica if control else 0,
            'glucosa': control.bs_azucar_sangre if control else 0,
            'temperatura': control.temperatura_corporal if control else 0,
            'ritmo_cardiaco': control.frecuencia_cardiaca if control else 0
        }
    }
    
    return jsonify(datos_paciente), 200

@auth_bp.route('/api/predecir', methods=['POST'])
def predecir_riesgo():
    """ 
    PATRÓN FACADE: El frontend solo envía los signos vitales. 
    Este endpoint se encarga de hablar con el Singleton de IA y devolver la respuesta.
    """
    datos = request.get_json()
    signos_vitales = datos.get('signos_vitales')
    id_paciente = datos.get('id_paciente')

    if not signos_vitales or not id_paciente:
        return jsonify({'error': 'Faltan datos para procesar el diagnóstico'}), 400

    control = ControlPrenatal.query.filter_by(id_paciente=id_paciente).first()
    if not control:
        return jsonify({'error': 'No se encontró un registro de control prenatal para este paciente.'}), 404

    # ========================================================
    # 1. LÓGICA DE AHORRO: Verificar si ya existe diagnóstico
    # ========================================================
    diag_existente = DiagnosticoRiesgo.query.filter_by(id_control=control.id_control).first()
    
    if diag_existente and diag_existente.id_regla:
        # Si ya existe, buscamos la regla asociada y devolvemos sin usar la IA
        regla = ReglaClasificacion.query.get(diag_existente.id_regla)
        if regla:
            print("♻️ Retornando diagnóstico desde Base de Datos (Ahorro de IA)")
            return jsonify({
                "enfermedad_predicha": regla.enfermedad_predicha,
                "justificacion": regla.descripcion,
                "recomendacion_medica": "Continuar con el monitoreo establecido en el expediente.", # Texto por defecto ya que no lo guardamos en BD
                "nivel_riesgo": diag_existente.nivel_riesgo,
                "confianza_ia": float(diag_existente.confianza_modelo) if diag_existente.confianza_modelo else 95,
                "alerta_glucosa": regla.alerta_glucosa
            }), 200

    # ========================================================
    # 2. SI ES NUEVA: Llamamos a la IA y guardamos
    # ========================================================
    oraculo = AIService()
    dictamen = oraculo.predecir_riesgo_clinico(signos_vitales)

    if dictamen:
        try:
            nueva_regla = ReglaClasificacion(
                enfermedad_predicha=dictamen['enfermedad_predicha'],
                descripcion=dictamen['justificacion'],
                alerta_glucosa=dictamen.get('alerta_glucosa', 'Sin alerta específica.')
            )
            db.session.add(nueva_regla)
            db.session.flush()

            nuevo_diagnostico = DiagnosticoRiesgo(
                id_control=control.id_control,
                id_regla=nueva_regla.id_regla,
                nivel_riesgo=dictamen['nivel_riesgo'],
                confianza_modelo=dictamen['confianza_ia']
            )
            db.session.add(nuevo_diagnostico)
            db.session.commit()

            return jsonify(dictamen), 200

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error crítico en SQL: {e}")
            return jsonify({'error': 'La IA respondió, pero la Base de Datos falló al guardar.'}), 500
    else:
        return jsonify({'error': 'Servicio de IA saturado por límite de consultas. Reintente en 1 minuto.'}), 500
from flask import Blueprint, request, jsonify
from app.models import db, Usuario, SesionOTP, Administrador
from app.services.email_service import enviar_correo_otp
import random
from datetime import datetime, timedelta, timezone

auth_bp = Blueprint('auth', __name__)

def generar_codigo_6_digitos():
    return str(random.randint(100000, 999999))

@auth_bp.route('/api/auth/solicitar-otp', methods=['POST'])
def solicitar_otp():
    datos = request.get_json()
    correo = datos.get('correo')
    
    if not correo:
        return jsonify({'error': 'El correo es obligatorio'}), 400

    # 1. Buscar o crear el usuario (Médico)
    usuario = Usuario.query.filter_by(correo_institucional=correo).first()
    
    if not usuario:
        # Si no existe, es un flujo de registro
        nombre = datos.get('nombre', 'Usuario')
        apellido = datos.get('apellido', 'Pendiente')
        especialidad = datos.get('especialidad', 'General')
        
        usuario = Usuario(
            nombres=nombre,
            apellidos=apellido,
            correo_institucional=correo,
            especialidad=especialidad
        )
        db.session.add(usuario)
        db.session.commit()

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

    # 4. Enviar el código
    if enviar_correo_otp(correo, codigo):
        return jsonify({'mensaje': 'Código enviado exitosamente', 'correo': correo}), 200
    else:
        return jsonify({'error': 'Error al procesar el envío'}), 500
    
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

    return jsonify({
        'mensaje': 'Autenticación exitosa',
        'usuario': {
            'nombre_completo': f"{usuario.nombres} {usuario.apellidos}",
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
    
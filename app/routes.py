from flask import Blueprint, request, jsonify
from app.models import db, Usuario, SesionOTP
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
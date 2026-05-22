from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

# Inicializamos SQLAlchemy
db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    correo_institucional = db.Column(db.String(255), unique=True, nullable=False)
    especialidad = db.Column(db.String(100))
    estado_activo = db.Column(db.Boolean, default=True, nullable=False)
    fecha_registro = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone.utc))
    
    # Relaciones
    sesiones = db.relationship('SesionOTP', backref='usuario', lazy=True)
    controles = db.relationship('ControlPrenatal', backref='medico', lazy=True)

class SesionOTP(db.Model):
    __tablename__ = 'sesion_otp'
    id_sesion = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    codigo_otp = db.Column(db.String(10), nullable=False)
    fecha_expiracion = db.Column(db.DateTime(timezone=True), nullable=False)
    usado = db.Column(db.Boolean, default=False, nullable=False)
    intentos_fallidos = db.Column(db.Integer, default=0, nullable=False)

class DatasetCrudo(db.Model):
    __tablename__ = 'dataset_crudo'
    id_raw = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer)
    systolic_bp = db.Column(db.Numeric(5,1))
    diastolic_bp = db.Column(db.Numeric(5,1))
    bs = db.Column(db.Numeric(6,2))
    body_temp = db.Column(db.Numeric(4,1))
    heart_rate = db.Column(db.Integer)
    risk_level = db.Column(db.String(50))
    procesado = db.Column(db.Boolean, default=False) # La IA lo cambiará a True al leerlo

class PacienteSintetica(db.Model):
    __tablename__ = 'paciente_sintetica'
    id_paciente = db.Column(db.Integer, primary_key=True)
    identificacion_ficticia = db.Column(db.String(20), unique=True, nullable=False)
    nombres_ficticios = db.Column(db.String(100), nullable=False)
    apellidos_ficticios = db.Column(db.String(100), nullable=False)
    edad = db.Column(db.Integer)
    
    # Relación con sus controles prenatales
    controles = db.relationship('ControlPrenatal', backref='paciente', lazy=True)

class ControlPrenatal(db.Model):
    __tablename__ = 'control_prenatal'
    id_control = db.Column(db.Integer, primary_key=True)
    id_paciente = db.Column(db.Integer, db.ForeignKey('paciente_sintetica.id_paciente'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    fecha_consulta = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone.utc))
    semanas_gestacion = db.Column(db.Integer, nullable=False)
    presion_sistolica = db.Column(db.Numeric(5,1), nullable=False)
    presion_diastolica = db.Column(db.Numeric(5,1), nullable=False)
    bs_azucar_sangre = db.Column(db.Numeric(6,2))
    temperatura_corporal = db.Column(db.Numeric(4,1))
    frecuencia_cardiaca = db.Column(db.Integer)
    peso = db.Column(db.Float, nullable=True)

    # Relación 1 a 1 con el diagnóstico
    diagnostico = db.relationship('DiagnosticoRiesgo', backref='control', uselist=False)

class ReglaClasificacion(db.Model):
    __tablename__ = 'regla_clasificacion'
    id_regla = db.Column(db.Integer, primary_key=True)
    nombre_regla = db.Column(db.String(100), nullable=False)
    condicion_variable = db.Column(db.String(50), nullable=False)
    operador = db.Column(db.String(10), nullable=False)
    valor_umbral = db.Column(db.Numeric(8,2), nullable=False)
    nivel_riesgo_asignado = db.Column(db.String(20), nullable=False)
    complicacion_probable = db.Column(db.String(150))
    activa = db.Column(db.Boolean, default=True, nullable=False)

class DiagnosticoRiesgo(db.Model):
    __tablename__ = 'diagnostico_riesgo'
    id_diagnostico = db.Column(db.Integer, primary_key=True)
    id_control = db.Column(db.Integer, db.ForeignKey('control_prenatal.id_control'), unique=True, nullable=False)
    nivel_riesgo = db.Column(db.String(20), nullable=False)
    confianza_modelo = db.Column(db.Numeric(5,2))

class Administrador(db.Model):
    __tablename__ = 'administrador'
    id_admin = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False) # Texto plano temporal para cumplir requerimiento directo (12345)
    nombre_completo = db.Column(db.String(100), nullable=False)
import os
import sys
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# --- AJUSTE CLAVE PARA VERCEL Y ESTRUCTURAS MODULARES ---
# Esto asegura que Python entienda dónde está la carpeta 'app'
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importamos la base de datos y los modelos desde la carpeta 'app'
from app.models import db, Usuario, SesionOTP, DatasetCrudo, PacienteSintetica, ControlPrenatal, ReglaClasificacion, DiagnosticoRiesgo, Administrador
from app.services.ai_service import AIService

# Cargar variables de entorno del archivo .env
load_dotenv()

app = Flask(__name__)

# ==========================================
# 1. CONFIGURACIÓN DE CORS (Seguridad Cross-Domain)
# ==========================================
dominios_permitidos = [
    "http://localhost:5500", 
    "http://127.0.0.1:5500", 
    "https://materchild-frontend.vercel.app" # NOTA: Recuerda cambiar esto por tu URL real de Vercel
]
CORS(app, resources={r"/api/*": {"origins": dominios_permitidos}})

# ==========================================
# 2. CABECERAS DE SEGURIDAD (Solución alertas QA)
# ==========================================
@app.after_request
def aplicar_cabeceras_seguridad(response):
    # Soluciona la alerta de Content Security Policy (CSP)
    response.headers['Content-Security-Policy'] = "default-src 'self';"
    
    # Soluciona la filtración de versión ocultando que usamos Werkzeug/Flask
    response.headers['Server'] = "MaterChild Predic Server"
    
    # Cabeceras extra de protección (Clickjacking y MIME-sniffing)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    
    return response

# Configuración de la base de datos apuntando a Neon.tech
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Vinculamos la app con SQLAlchemy
db.init_app(app)

# Registro de rutas de autenticación
from app.routes import auth_bp
app.register_blueprint(auth_bp)

# Registro de rutas de datos de dataset
from app.data_routes import data_bp
app.register_blueprint(data_bp)

# ESTO CREA LAS TABLAS EN NEON SI NO EXISTEN AÚN
with app.app_context():
    db.create_all()
    print("Tablas verificadas/creadas en Neon.tech exitosamente.")

@app.route('/api/estado', methods=['GET'])
def estado():
    try:
        usuarios_count = Usuario.query.count()
        return jsonify({
            "sistema": "Materchild Predic",
            "estado": "Backend y Base de Datos Operativos",
            "usuarios_registrados": usuarios_count
        })
    except Exception as e:
         return jsonify({"error": "No se pudo conectar a la base de datos", "detalle": str(e)}), 500

# Despertamos a la IA para verificar la conexión
oraculo = AIService()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
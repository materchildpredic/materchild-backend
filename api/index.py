import os
import sys
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# --- AJUSTE CLAVE PARA VERCEL Y ESTRUCTURAS MODULARES ---
# Esto asegura que Python entienda dónde está la carpeta 'app'
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importamos la base de datos y los modelos desde la carpeta 'app'
from app.models import db, Usuario, SesionOTP, DatasetCrudo, PacienteSintetica, ControlPrenatal, ReglaClasificacion, DiagnosticoRiesgo
from app.services.ai_service import AIService

# Cargar variables de entorno del archivo .env
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuración de la base de datos apuntando a Neon.tech
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Vinculamos la app con SQLAlchemy
db.init_app(app)

from app.routes import auth_bp
app.register_blueprint(auth_bp)

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
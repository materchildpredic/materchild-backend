from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Permitir que el Frontend se conecte sin problemas de seguridad locales
CORS(app) 

@app.route('/api/estado', methods=['GET'])
def estado():
    return jsonify({
        "sistema": "Materchild Predic", 
        "estado": "Backend Operativo Localmente"
    })

# Esto solo se ejecuta cuando pruebas en tu PC
if __name__ == '__main__':
    app.run(debug=True, port=5000)
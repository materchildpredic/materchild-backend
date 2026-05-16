from flask import Blueprint, request, jsonify
from app.models import db, DatasetCrudo
import csv
import io

# Creamos un nuevo Blueprint para todo lo relacionado con datos
data_bp = Blueprint('data', __name__)

@data_bp.route('/api/data/upload-dataset', methods=['POST'])
def upload_dataset():
    if 'file' not in request.files:
        return jsonify({'error': 'No se encontró ningún archivo en la petición'}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
        
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'El archivo debe tener extensión .csv'}), 400
        
    try:
        # CAMBIO CLAVE 1: Usamos "utf-8-sig" para limpiar los caracteres invisibles de Excel
        contenido = file.stream.read().decode("utf-8-sig")
        stream = io.StringIO(contenido, newline=None)
        
        csv_reader = csv.DictReader(stream, delimiter=';')
        
        registros_agregados = 0
        numero_fila = 1 # Empezamos a contar desde la fila 1 (el encabezado)
        
        for row in csv_reader:
            numero_fila += 1
            
            # CAMBIO CLAVE 2: Si la fila está vacía, la ignoramos y pasamos a la siguiente
            if not row or not row.get('Age') or str(row.get('Age')).strip() == '':
                continue
                
            try:
                nuevo_registro = DatasetCrudo(
                    age=int(row['Age']),
                    systolic_bp=float(row['SystolicBP']),
                    diastolic_bp=float(row['DiastolicBP']),
                    bs=float(row['BS']),
                    body_temp=float(row['BodyTemp']),
                    heart_rate=int(row['HeartRate']),
                    risk_level=row['RiskLevel'].strip(),
                    procesado=False
                )
                db.session.add(nuevo_registro)
                registros_agregados += 1
                
            except ValueError as ve:
                db.session.rollback()
                return jsonify({'error': f'Error en la fila {numero_fila}: Hay un texto o espacio donde debería ir un número. (Detalle: {str(ve)})'}), 400
            except KeyError as ke:
                db.session.rollback()
                return jsonify({'error': f'Error en el encabezado: No se encontró la columna exacta {str(ke)}.'}), 400

        # Guardamos todo
        db.session.commit()
        
        return jsonify({
            'mensaje': 'Dataset cargado exitosamente',
            'registros_insertados': registros_agregados
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error general al procesar: {str(e)}'}), 500
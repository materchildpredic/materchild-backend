from flask import Blueprint, request, jsonify
from app.models import db, DatasetCrudo, PacienteSintetica, ControlPrenatal, Usuario
from app.services.ai_service import AIService
import csv
import io
import random


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
    
@data_bp.route('/api/data/procesar-lote', methods=['POST'])
def procesar_lote_crudo():
    datos = request.get_json() or {}
    tamano_lote = datos.get('lote', 50) 

    registros_pendientes = DatasetCrudo.query.filter_by(procesado=False).limit(tamano_lote).all()

    if not registros_pendientes:
        return jsonify({'mensaje': 'No hay más registros pendientes por procesar.'}), 200

    cantidad_encontrada = len(registros_pendientes)

    oraculo = AIService()
    identidades = oraculo.generar_identidades_sinteticas(cantidad_encontrada)

    if not identidades or len(identidades) != cantidad_encontrada:
        return jsonify({'error': 'La IA falló al generar las identidades. Intenta de nuevo.'}), 500

    usuario_responsable = Usuario.query.first()
    if not usuario_responsable:
        return jsonify({'error': 'Debe existir al menos un usuario/médico registrado en el sistema.'}), 400

    pacientes_creadas = 0

    try:
        for i, crudo in enumerate(registros_pendientes):
            identidad = identidades[i]

            # 1. Python genera la cédula única y aleatoria
            cedula_segura = str(random.randint(1000000000, 9999999999))

            # 2. Extraemos los nombres de forma segura con .get() para evitar KeyErrors
            nombres = identidad.get('nombres_ficticios', 'Paciente')
            apellidos = identidad.get('apellidos_ficticios', 'Generada')

            # 3. Creamos a la paciente combinando la cédula de Python y los nombres de la IA
            nueva_paciente = PacienteSintetica(
                identificacion_ficticia=cedula_segura,
                nombres_ficticios=nombres,
                apellidos_ficticios=apellidos,
                edad=crudo.age
            )
            db.session.add(nueva_paciente)
            db.session.flush() # Guardamos temporalmente para obtener el ID

            # 4. Creamos el control prenatal con los datos del CSV
            nuevo_control = ControlPrenatal(
                id_paciente=nueva_paciente.id_paciente,
                id_usuario=usuario_responsable.id_usuario,
                semanas_gestacion=30,
                presion_sistolica=crudo.systolic_bp,
                presion_diastolica=crudo.diastolic_bp,
                bs_azucar_sangre=crudo.bs,
                temperatura_corporal=crudo.body_temp,
                frecuencia_cardiaca=crudo.heart_rate
            )
            db.session.add(nuevo_control)

            # 5. Marcamos como procesado
            crudo.procesado = True
            pacientes_creadas += 1

        db.session.commit()

        restantes = DatasetCrudo.query.filter_by(procesado=False).count()

        return jsonify({
            'mensaje': f'Se estructuraron {pacientes_creadas} pacientes exitosamente.',
            'restantes': restantes
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error en base de datos al cruzar datos: {str(e)}'}), 500
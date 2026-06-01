import threading
import smtplib
import os
from email.message import EmailMessage
from fpdf import FPDF
from datetime import datetime

# ==========================================
# SUBSISTEMA 1: Generador de PDF
# ==========================================
class GeneradorPDF:
    def crear_reporte(self, datos_paciente, dictamen):
        pdf = FPDF()
        pdf.add_page()
        
        # Colores Institucionales (Usando RGB)
        COLOR_PRIMARIO = (13, 110, 253) # Azul
        COLOR_TEXTO = (50, 50, 50)
        COLOR_ALERTA = (220, 53, 69) if dictamen['nivel_riesgo'] == 'Alto' else (25, 135, 84)

        
        # Pon esto en GeneradorPDF donde configuramos la ruta:
        base_dir = os.path.abspath(os.path.dirname(__file__)) # Se ubica en app/services
        ruta_logo = os.path.join(base_dir, '..', '..', 'assets', 'logo.png') # Sube a la raíz y entra a assets

        if os.path.exists(ruta_logo):
            pdf.image(ruta_logo, x=10, y=8, w=30)
            
        # Encabezado Institucional
        pdf.set_font("Helvetica", style="B", size=16)
        pdf.set_text_color(*COLOR_PRIMARIO)
        pdf.cell(0, 10, "Materchild Predic - Salud Materno Infantil", ln=True, align="R")
        pdf.set_font("Helvetica", size=10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, "Reporte Oficial de Investigación Clínica Sintética", ln=True, align="R")
        pdf.cell(0, 5, f"Fecha de emisión: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="R")
        pdf.ln(15)

        # Datos del Paciente Sintético
        pdf.set_font("Helvetica", style="B", size=12)
        pdf.set_text_color(*COLOR_TEXTO)
        pdf.cell(0, 10, f"Paciente: {datos_paciente['nombre_completo']} (ID: {datos_paciente['identificacion']})", ln=True)
        pdf.cell(0, 5, f"Edad: {datos_paciente['edad']} años", ln=True)
        pdf.ln(5)

        # Sección de Diagnóstico
        pdf.set_font("Helvetica", style="B", size=14)
        pdf.set_text_color(*COLOR_TEXTO)
        pdf.cell(0, 10, "1. DICTAMEN PREDICTIVO (IA)", ln=True, border='B')
        pdf.ln(5)
        
        pdf.set_font("Helvetica", style="B", size=12)
        pdf.cell(50, 8, "Enfermedad Predicha: ", border=0)
        pdf.set_font("Helvetica", size=12)
        pdf.cell(0, 8, dictamen['enfermedad_predicha'], ln=True)
        
        pdf.set_font("Helvetica", style="B", size=12)
        pdf.cell(50, 8, "Nivel de Riesgo: ", border=0)
        pdf.set_font("Helvetica", style="B", size=12)
        pdf.set_text_color(*COLOR_ALERTA)
        pdf.cell(0, 8, f"{dictamen['nivel_riesgo']} ({dictamen['confianza_ia']}% de confianza)", ln=True)
        
        # Justificación
        pdf.ln(5)
        pdf.set_text_color(*COLOR_TEXTO)
        pdf.set_font("Helvetica", style="B", size=11)
        pdf.cell(0, 6, "Justificación Médica:", ln=True)
        pdf.set_font("Helvetica", size=10)
        pdf.multi_cell(0, 6, dictamen['justificacion'])
        
        # Guardar en memoria/archivo temporal
        ruta_pdf = f"reporte_temporal_{datos_paciente['identificacion']}.pdf"
        pdf.output(ruta_pdf)
        return ruta_pdf

# ==========================================
# SUBSISTEMA 2: Servicio de Correo SMTP
# ==========================================
class ServicioCorreo:
    def enviar(self, destinatario, ruta_pdf):
        # Tomamos las credenciales seguras de tu archivo .env
        REMITENTE = os.getenv('EMAIL_USUARIO') 
        PASSWORD = os.getenv('EMAIL_CONTRASENA')

        msg = EmailMessage()
        msg['Subject'] = 'Materchild Predic - Diagnóstico IA Generado'
        msg['From'] = REMITENTE
        msg['To'] = destinatario
        msg.set_content("Estimado especialista,\n\nAdjunto encontrará el dictamen clínico generado por la plataforma Materchild Predic" \
        " para su revisión.\n\nSistema Seguro de Datos Sintéticos Materchild.")

        # Adjuntar PDF
        with open(ruta_pdf, 'rb') as f:
            pdf_data = f.read()
        msg.add_attachment(pdf_data, maintype='application', subtype='pdf', filename='Dictamen_Clinico.pdf')

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(REMITENTE, PASSWORD)
                server.send_message(msg)
            print("✅ Correo enviado exitosamente.")
        except Exception as e:
            print(f"❌ Error enviando correo: {e}")
        finally:
            # Limpieza del archivo temporal
            if os.path.exists(ruta_pdf):
                os.remove(ruta_pdf)

# ==========================================
# FACADE: Orquestador y Automatizador (Background Task)
# ==========================================
class ReporteFacade:
    def __init__(self):
        self.generador_pdf = GeneradorPDF()
        self.servicio_correo = ServicioCorreo()

    def _tarea_en_segundo_plano(self, datos_paciente, dictamen, correo_destino):
        """Esta función se ejecuta en las sombras (Threading)"""
        print("Iniciando automatización en segundo plano...")
        ruta_pdf = self.generador_pdf.crear_reporte(datos_paciente, dictamen)
        self.servicio_correo.enviar(correo_destino, ruta_pdf)

    def automatizar_envio(self, datos_paciente, dictamen, correo_destino):
        """Punto de entrada del Facade. Desencadena el Threading."""
        # AUTOMATIZADOR DE PYTHON: Creamos un hilo independiente
        hilo = threading.Thread(target=self._tarea_en_segundo_plano, args=(datos_paciente, dictamen, correo_destino))
        hilo.start()
        return True
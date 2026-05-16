import smtplib
from email.mime.text import MIMEText
import os

def enviar_correo_otp(destinatario, codigo_otp):
    # Intentamos leer las credenciales del archivo .env
    remitente = os.getenv('SMTP_USER')
    password = os.getenv('SMTP_PASSWORD')

    # MODO SIMULACIÓN: Si no hay credenciales, imprimimos en la terminal
    if not remitente or not password:
        print("\n" + "📧" + "="*50)
        print(f"⚠️  [MODO DESARROLLO] Simulación de envío de correo")
        print(f"PARA: {destinatario}")
        print(f"CÓDIGO DE ACCESO: {codigo_otp}")
        print("="*52 + "\n")
        return True

    # MODO REAL: Envío por SMTP (ej. Gmail)
    msg = MIMEText(f"Bienvenido a Materchild Predic.\n\nTu código de acceso seguro es: {codigo_otp}\n\nEste código expirará en 10 minutos.")
    msg['Subject'] = 'Código de Acceso - Materchild Predic'
    msg['From'] = remitente
    msg['To'] = destinatario

    try:
        # Configuración estándar para Gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remitente, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"❌ Error en envío real: {e}")
        return False
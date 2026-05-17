import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def enviar_correo_otp(destinatario, codigo_otp):
    """
    Se conecta al servidor SMTP de Outlook y envía el código OTP con diseño HTML.
    """
    smtp_user = os.getenv("EMAIL_USUARIO")
    smtp_pass = os.getenv("EMAIL_CONTRASENA")

    # Configuración del servidor de GMAIL
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    if not smtp_user or not smtp_pass:
        print("⚠️ MODO SIMULACIÓN: Faltan credenciales en el .env. El código es:", codigo_otp)
        return True # Retorna True para que el sistema no colapse si olvidas la contraseña

    # Creamos el mensaje
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = destinatario
    msg['Subject'] = "Código de Acceso - Materchild Predic"

    # Diseño del correo (Plantilla HTML)
    # Diseño del correo (Plantilla HTML basada en el UI de Materchild)
    html = f"""
    <div style="font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; background-color: #f4f6f9; padding: 40px 20px; margin: 0;">
        <div style="max-width: 550px; margin: 0 auto; background-color: #ffffff; border-radius: 24px; overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);">
            
            <div style="background-color: #006579; padding: 40px 20px; text-align: center;"> 
                <div style="background-color: #ffffff; width: 70px; height: 70px; border-radius: 50%; margin: 0 auto 15px auto; display: flex; align-items: center; justify-content: center; overflow: hidden; border: 2px solid rgba(255,255,255,0.2);">
                    <span style="color: #006579; font-size: 24px; font-weight: bold; line-height: 70px; display: block;">MP</span>
                </div>
                <h2 style="color: #ffffff; margin: 0; font-size: 22px; font-weight: 700; letter-spacing: 0.5px;">Materchild Predic</h2>
                <p style="color: rgba(255, 255, 255, 0.85); margin: 10px 0 0 0; font-size: 14px;">Plataforma Predictiva de Salud</p>
            </div>
            
            <div style="padding: 40px 30px; text-align: center;">
                <h3 style="color: #1e293b; margin-top: 0; font-size: 20px; font-weight: 700;">Verificación de Identidad</h3>
                <p style="color: #64748b; font-size: 15px; line-height: 1.6; margin-bottom: 30px;">
                    Ha solicitado ingresar a la plataforma clínica. Utilice el siguiente código de un solo uso (OTP) para continuar con su acceso seguro:
                </p>
                
                <div style="background-color: #f8fafc; border: 1px solid #cbd5e1; border-radius: 12px; padding: 20px; margin: 0 auto; max-width: 250px;">
                    <h1 style="color: #006579; font-size: 42px; letter-spacing: 8px; margin: 0; font-weight: 800;">{codigo_otp}</h1>
                </div>
                
                <p style="color: #94a3b8; font-size: 12px; margin-top: 40px; line-height: 1.5;">
                    <strong style="color: #64748b;">Este código expirará en 10 minutos.</strong><br>
                    Si usted no solicitó este acceso, por favor ignore este correo para mantener la seguridad de su cuenta.
                </p>
            </div>
            
        </div>
        
        <div style="text-align: center; margin-top: 20px;">
            <p style="color: #94a3b8; font-size: 12px; margin: 0;">© 2026 Materchild Predic. Todos los derechos reservados.</p>
        </div>
    </div>
    """
    
    msg.attach(MIMEText(html, 'html'))

    try:
        # Conexión segura con Gmail
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls() # Activa el cifrado de seguridad
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, destinatario, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"❌ Error real en el servidor SMTP de Gmail: {e}")
        return False
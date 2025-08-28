# ========== backend/app/services/notification_service.py ==========
"""
Sistema de notificaciones (WhatsApp/Email/Telegram)
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import asyncio
import aiohttp
from pathlib import Path
from datetime import datetime

from ..core.config import settings

class NotificationService:
    def __init__(self):
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.email_user = settings.smtp_user
        self.email_password = settings.smtp_password
        
        # Twilio para WhatsApp
        self.twilio_sid = settings.twilio_account_sid
        self.twilio_token = settings.twilio_auth_token
        self.twilio_whatsapp_from = settings.twilio_whatsapp_from
        
        # Telegram
        self.telegram_token = settings.telegram_bot_token
    
    async def send_email(self, to_email: str, subject: str, body: str, attachment_path: str = None):
        """Enviar notificación por email"""
        print("\n--- PASO 4: Dentro del Servicio de Email ---")
        print(f"👤 Usuario SMTP: {self.email_user}")
        print(f"🔑 Contraseña SMTP: {'Sí' if self.email_password else 'NO (¡Falta en .env!)'}")
        print(f"🌍 Servidor SMTP: {self.smtp_server}:{self.smtp_port}")
        
        if not self.email_user or not self.email_password:
            print("⚠️ ERROR: Faltan credenciales de email en el archivo .env")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            # Agregar adjunto si existe
            if attachment_path and Path(attachment_path).exists():
                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {Path(attachment_path).name}'
                    )
                    msg.attach(part)
            
            # Enviar email
            print(f"📬 Intentando conectar y enviar email a {to_email}...")
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_user, to_email, text)
            server.quit()
            
            print(f"✔️ Email enviado exitosamente a {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ ERROR CRÍTICO AL ENVIAR EMAIL: {e}")
            return False
    
    async def send_whatsapp(self, to_number: str, message: str):
        """Enviar mensaje por WhatsApp usando Twilio"""
        if not self.twilio_sid or not self.twilio_token:
            print("⚠️ Configuración de Twilio no encontrada")
            return False
        
        try:
            # Formatear número de teléfono
            if not to_number.startswith('whatsapp:'):
                to_number = f"whatsapp:{to_number}"
            
            # URL de la API de Twilio
            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_sid}/Messages.json"
            
            auth = aiohttp.BasicAuth(self.twilio_sid, self.twilio_token)
            data = {
                'From': self.twilio_whatsapp_from,
                'To': to_number,
                'Body': message
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, auth=auth, data=data) as response:
                    if response.status == 201:
                        print(f"📱 WhatsApp enviado a {to_number}")
                        return True
                    else:
                        print(f"❌ Error enviando WhatsApp: {response.status}")
                        return False
                        
        except Exception as e:
            print(f"❌ Error enviando WhatsApp: {e}")
            return False
    
    async def send_telegram(self, chat_id: str, message: str):
        """Enviar mensaje por Telegram"""
        if not self.telegram_token:
            print("⚠️ Token de Telegram no encontrado")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        print(f"📱 Telegram enviado a {chat_id}")
                        return True
                    else:
                        print(f"❌ Error enviando Telegram: {response.status}")
                        return False
                        
        except Exception as e:
            print(f"❌ Error enviando Telegram: {e}")
            return False
    
    async def notify_job_completed(self, job_name: str, output_path: str, recipient: str):
        """Notificar trabajo completado"""
        subject = f"🎬 Render Completado: {job_name}"
        body = f"""¡Hola!

El trabajo de render '{job_name}' ha sido completado exitosamente.

📁 Archivos de salida: {output_path}
⏰ Completado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

¡Tu render está listo!

Saludos,
Render_QM System
"""
        
        await self.send_email(recipient, subject, body)
    
    async def notify_job_failed(self, job_name: str, error_message: str, recipient: str):
        """Notificar trabajo fallido"""
        subject = f"❌ Error en Render: {job_name}"
        body = f"""Hola,

El trabajo de render '{job_name}' ha fallado.

❌ Error: {error_message}
⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Por favor revisa la configuración y vuelve a intentarlo.

Saludos,
Render_QM System
"""
        
        await self.send_email(recipient, subject, body)
    
    async def notify_node_offline(self, node_name: str, ip_address: str, recipients: list):
        """Notificar nodo offline"""
        subject = f"🔴 Nodo Offline: {node_name}"
        body = f"""Alerta del Sistema,

El nodo de render '{node_name}' ({ip_address}) se ha desconectado.

⏰ Detectado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Por favor verifica la conectividad del nodo.

Saludos,
Render_QM System
"""
        
        for recipient in recipients:
            await self.send_email(recipient, subject, body)

# Instancia global del servicio de notificaciones
notification_service = NotificationService()

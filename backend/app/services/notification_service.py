"""
Sistema de notificaciones (WhatsApp/Email/Telegram) para Render_QM.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import asyncio
import aiohttp
from pathlib import Path

from app.core.config import settings


class NotificationService:
    def __init__(self) -> None:
        self.smtp_server = getattr(settings, "smtp_server", None)
        self.smtp_port = getattr(settings, "smtp_port", 587)
        self.email_user = (
            getattr(settings, "smtp_user", None)
            or getattr(settings, "smtp_username", None)
        )
        self.email_password = getattr(settings, "smtp_password", None)
        self.email_from = (
            getattr(settings, "smtp_from_email", None)
            or getattr(settings, "email_from", None)
            or self.email_user
        )
        self.twilio_sid = getattr(settings, "twilio_account_sid", None)
        self.twilio_token = getattr(settings, "twilio_auth_token", None)
        self.twilio_whatsapp_from = getattr(settings, "twilio_whatsapp_from", None)
        self.telegram_token = getattr(settings, "telegram_bot_token", None)

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        attachment_path: str | None = None,
    ) -> bool:
        if not self.smtp_server or not self.email_user or not self.email_password:
            print("⚠️ Configuración de email/SMTP no encontrada o incompleta")
            return False

        try:
            msg = MIMEMultipart()
            msg["From"] = self.email_from or self.email_user
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            if attachment_path and Path(attachment_path).exists():
                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename={Path(attachment_path).name}",
                    )
                    msg.attach(part)

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_from or self.email_user, to_email, text)
            server.quit()

            print(f"📧 Email enviado a {to_email}")
            return True

        except Exception as e:
            print(f"❌ Error enviando email: {e}")
            return False

    async def send_whatsapp(self, to_number: str, message: str) -> bool:
        if not self.twilio_sid or not self.twilio_token or not self.twilio_whatsapp_from:
            print("⚠️ Configuración de Twilio no encontrada o incompleta")
            return False

        try:
            if not to_number.startswith("whatsapp:"):
                to_number = f"whatsapp:{to_number}"

            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_sid}/Messages.json"
            auth = aiohttp.BasicAuth(self.twilio_sid, self.twilio_token)
            data = {
                "From": self.twilio_whatsapp_from,
                "To": to_number,
                "Body": message,
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, auth=auth, data=data) as response:
                    if response.status in (200, 201):
                        print(f"📱 WhatsApp enviado a {to_number}")
                        return True
                    else:
                        text = await response.text()
                        print(f"❌ Error enviando WhatsApp: status={response.status} body={text}")
                        return False

        except Exception as e:
            print(f"❌ Error enviando WhatsApp: {e}")
            return False

    async def send_telegram(self, chat_id: str, message: str) -> bool:
        if not self.telegram_token:
            print("⚠️ Token de Telegram no encontrado")
            return False

        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown",
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        print(f"📱 Telegram enviado a {chat_id}")
                        return True
                    else:
                        text = await response.text()
                        print(f"❌ Error enviando Telegram: status={response.status} body={text}")
                        return False

        except Exception as e:
            print(f"❌ Error enviando Telegram: {e}")
            return False

    async def notify_job_completed(
        self,
        job_name: str,
        output_path: str,
        recipient: str,
    ) -> None:
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

    async def notify_job_failed(
        self,
        job_name: str,
        error_message: str,
        recipient: str,
    ) -> None:
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

    async def notify_node_offline(
        self,
        node_name: str,
        ip_address: str,
        recipients: list[str],
    ) -> None:
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


notification_service = NotificationService()

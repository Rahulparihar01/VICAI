import logging
import smtplib
from email.message import EmailMessage

from app.core.config import Settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def send_welcome_email(self, email: str, password: str, role: str, frontend_url: str) -> None:
        if not self.settings.smtp_host or not self.settings.smtp_from_email:
            logger.warning(
                f"SMTP not configured. Would have sent welcome email to {email} "
                f"with role {role}. Credentials: {email} / {password}"
            )
            return

        msg = EmailMessage()
        msg["Subject"] = "Welcome to VicAI"
        msg["From"] = self.settings.smtp_from_email
        msg["To"] = email

        content = f"""
Welcome to VicAI!

An account has been created for you with the role of {role}.

You can log in using the following credentials:
Email: {email}
Password: {password}

Please log in here: {frontend_url}

For security reasons, we recommend changing your password after logging in.

Best regards,
The VicAI Team
"""
        msg.set_content(content)

        try:
            with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port) as server:
                server.starttls()
                if self.settings.smtp_user and self.settings.smtp_password:
                    server.login(self.settings.smtp_user, self.settings.smtp_password.get_secret_value())
                server.send_message(msg)
            logger.info(f"Successfully sent welcome email to {email}")
        except Exception as e:
            logger.error(f"Failed to send welcome email to {email}: {e}")

    def send_password_reset_email(self, email: str, password: str, frontend_url: str) -> None:
        if not self.settings.smtp_host or not self.settings.smtp_from_email:
            logger.warning(
                f"SMTP not configured. Would have sent password reset email to {email}. Credentials: {email} / {password}"
            )
            return

        msg = EmailMessage()
        msg["Subject"] = "Your VicAI Password Has Been Reset"
        msg["From"] = self.settings.smtp_from_email
        msg["To"] = email

        content = f"""
Hello,

Your password for VicAI has been reset by an administrator.

You can log in using your new credentials:
Email: {email}
Password: {password}

Please log in here: {frontend_url}

For security reasons, we strongly recommend changing your password after logging in.

Best regards,
The VicAI Team
"""
        msg.set_content(content)

        try:
            with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port) as server:
                server.starttls()
                if self.settings.smtp_user and self.settings.smtp_password:
                    server.login(self.settings.smtp_user, self.settings.smtp_password.get_secret_value())
                server.send_message(msg)
            logger.info(f"Successfully sent password reset email to {email}")
        except Exception as e:
            logger.error(f"Failed to send password reset email to {email}: {e}")

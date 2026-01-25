from aiosmtplib import SMTP

from core.config import settings


async def create_smtp() -> SMTP:
    smtp = SMTP(
        hostname=settings.MAIL_SERVER,
        port=settings.MAIL_PORT,
        start_tls=settings.MAIL_STARTTLS,
        use_tls=settings.MAIL_SSL_TLS,
        validate_certs=settings.VALIDATE_CERTS,
        timeout=10,
    )
    await smtp.connect()
    await smtp.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
    return smtp

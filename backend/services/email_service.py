
from email.message import EmailMessage
from aiosmtplib import SMTP


class EmailService:
    def __init__(self, smtp: SMTP):
        self.smtp = smtp

    async def send(self, to: str, subject: str, body: str):
        msg = EmailMessage()
        msg["From"] = "axomjak@gmail.com"
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)

        await self.smtp.send_message(msg)
from email.message import EmailMessage
from aiosmtplib import SMTP
import random

class EmailService:
    def __init__(self, smtp: SMTP, sender: str):
        self.smtp = smtp
        self.sender = sender
        self.subject = "Confirming registration"

    async def send_verification_code(self, to: str, code: str):
        msg = EmailMessage()
        msg["From"] = self.sender
        msg["To"] = to
        msg["Subject"] = self.subject
        msg.set_content(f"Your verification code is: {code}.")

        await self.smtp.send_message(msg)

    @staticmethod
    def generate_code() -> str:
        return "".join(str(random.randint(0, 9)) for _ in range(6))
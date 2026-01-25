from email.message import EmailMessage
from aiosmtplib import SMTP
import random
from string import ascii_letters, digits


class EmailService:
    def __init__(self, smtp: SMTP, sender: str):
        self.smtp = smtp
        self.sender = sender
        self.subject = "Confirming registration"

    async def send(self, to: str):
        msg = EmailMessage()
        msg["From"] = self.sender
        msg["To"] = to
        msg["Subject"] = self.subject
        msg.set_content(self._generate_body())

        await self.smtp.send_message(msg)

    def _generate_body(self):
        code = self._generate_code()
        return f"Your verification code is {code}"

    @staticmethod
    def _generate_code():
        return "".join(random.choice(ascii_letters + digits) for _ in range(4))
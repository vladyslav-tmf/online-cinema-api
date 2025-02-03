import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from jinja2 import Environment, FileSystemLoader

from app.exceptions.email import BaseEmailError
from app.notifications.interfaces import EmailSenderInterface


class EmailSender(EmailSenderInterface):
    def __init__(
        self,
        hostname: str,
        port: int,
        email: str,
        password: str,
        use_tls: bool,
        template_dir: str,
        activation_email_template_name: str,
        activation_complete_email_template_name: str,
        password_email_template_name: str,
        password_complete_email_template_name: str,
        payment_success_email_template_name: str,
    ):
        self._hostname = hostname
        self._port = port
        self._email = email
        self._password = password
        self._use_tls = use_tls
        self._activation_email_template_name = activation_email_template_name
        self._activation_complete_email_template_name = (
            activation_complete_email_template_name
        )
        self._password_email_template_name = password_email_template_name
        self._password_complete_email_template_name = (
            password_complete_email_template_name
        )
        self._payment_success_email_template_name = payment_success_email_template_name

        self._env = Environment(loader=FileSystemLoader(template_dir))

    def _send_email(self, email: str, subject: str, html_content: str) -> None:
        message = MIMEMultipart()
        message["From"] = self._email
        message["To"] = email
        message["Subject"] = subject
        message.attach(MIMEText(html_content, "html"))

        try:
            with smtplib.SMTP(self._hostname, self._port) as server:
                if self._use_tls:
                    server.starttls()
                server.login(self._email, self._password)
                server.sendmail(self._email, email, message.as_string())
        except smtplib.SMTPException as error:
            logging.error(f"Failed to send email to {email}: {error}")
            raise BaseEmailError(f"Failed to send email to {email}: {error}")

    def send_activation_email(self, email: str, activation_link: str) -> None:
        template = self._env.get_template(self._activation_email_template_name)
        html_content = template.render(email=email, activation_link=activation_link)

        subject = "Account Activation"
        self._send_email(email, subject, html_content)

    def send_activation_complete_email(self, email: str, login_link: str) -> None:
        template = self._env.get_template(self._activation_complete_email_template_name)
        html_content = template.render(email=email, login_link=login_link)

        subject = "Account Activated Successfully"
        self._send_email(email, subject, html_content)

    def send_password_reset_email(self, email: str, reset_link: str) -> None:
        template = self._env.get_template(self._password_email_template_name)
        html_content = template.render(email=email, reset_link=reset_link)

        subject = "Password Reset Request"
        self._send_email(email, subject, html_content)

    def send_password_reset_complete_email(self, email: str, login_link: str) -> None:
        template = self._env.get_template(self._password_complete_email_template_name)
        html_content = template.render(email=email, login_link=login_link)

        subject = "Your Password Has Been Successfully Reset"
        self._send_email(email, subject, html_content)

    def send_payment_success_email(
        self, email: str, user_name: str, amount: str, watch_link: str
    ) -> None:
        template = self._env.get_template(self._payment_success_email_template_name)
        html_content = template.render(
            email=email, user_name=user_name, amount=amount, watch_link=watch_link
        )

        subject = "Payment Confirmation - Online Cinema"
        self._send_email(email, subject, html_content)

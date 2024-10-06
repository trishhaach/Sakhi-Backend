import logging
from django.core.mail import EmailMessage
from django.conf import settings
from smtplib import SMTPException

class Util:
    @staticmethod
    def send_email(data):
        try:
            email = EmailMessage(
                subject=data['subject'],
                body=data['body'],
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[data['to_email']]
            )
            email.send()  # Send the email
            logging.info(f"Email sent to {data['to_email']}")
        except SMTPException as smtp_error:
            logging.error(f"SMTP error occurred: {str(smtp_error)}")
            raise ValueError("Failed to send email due to SMTP error.")
        except Exception as e:
            logging.error(f"Failed to send email to {data['to_email']}: {str(e)}")
            raise ValueError("Failed to send email due to an unexpected error.")

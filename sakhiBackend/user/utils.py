import logging
from django.core.mail import EmailMessage
from django.conf import settings
from smtplib import SMTPException
from google.auth.transport import requests
from google.oauth2 import id_token
from user.models import User
from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed

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

class Google():
    @staticmethod
    def validate(access_token):
        try:
            id_info=id_token.verify_oauth2_token(access_token, requests.Request())
            if "user.google.com" in id_info['iss']:
                return id_info
            
        except Exception as e:
            return "token is invalid or has expired"
        
def register_social_user(provider, email, name):
    user=User._objects.filter(email=email)
    if user.exists():
        if provider == user[0].auth_provider:
            login_user=authenticate(email=email, password=settings.SOCIAL_AUTH_PASSWORD)
            return {
                
            }
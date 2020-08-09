from django.core.signing import Signer
from lastin.settings import ALLOWED_HOSTS
from django.template.loader import render_to_string


signer = Signer()

def send_user_activation_notification(user):
    """Отправка подтверждения регистрации на почту"""

    if ALLOWED_HOSTS:
        host = 'http://' + ALLOWED_HOSTS[0]
    else:
        host = 'http://localhost:8000'

    context = {'user': user, 'host': host,
               'sign': signer.sign(user.username) 
    }
    email_subject = render_to_string('email/activation_letter_subject.txt', context)
    email_body = render_to_string('email/activation_letter_body.txt', context)
    user.email_user(email_subject, email_body)
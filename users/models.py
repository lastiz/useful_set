from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import Signal

from .utilites import send_user_activation_notification


class AdvUser(AbstractUser):
    """Моя модель пользователя"""
    is_activated = models.BooleanField(default=True, db_index=True, verbose_name='Прошел активацию?')
    send_messages = models.BooleanField(default=True, verbose_name='Получать оповещения от сайта?')

    class Meta(AbstractUser.Meta):
        pass

#SIGNALS
user_registrated = Signal(providing_args=['instance'])

def user_registrated_dispatcher(sender, **kwargs):
    """Функция-диспатчер для сигнала регистрации нового
       пользователя. Отправляет письмо пользователю на емаил  
    """
    send_user_activation_notification(user=kwargs['instance'])

user_registrated.connect(user_registrated_dispatcher)
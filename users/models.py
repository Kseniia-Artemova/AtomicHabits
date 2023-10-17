from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель для описания пользователя"""

    username = None

    telegram_username = models.CharField(max_length=150, verbose_name='Уникальный идентификатор пользователя')

    USERNAME_FIELD = 'telegram_username'
    REQUIRED_FIELDS = []


from django.contrib.auth.models import AbstractUser
from django.db import models

from users.validators import TelegramNicknameValidator


class User(AbstractUser):
    """Модель для описания пользователя"""

    telegram_username = models.CharField(
        max_length=150,
        unique=True,
        validators=[TelegramNicknameValidator()],
        verbose_name='Уникальный идентификатор пользователя телеграм'
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['telegram_username']


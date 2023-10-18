from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible


@deconstructible
class TelegramNicknameValidator(RegexValidator):
    regex = r'^@[a-zA-Z0-9_]{4,31}$'
    message = 'Недопустимый ник Telegram.'


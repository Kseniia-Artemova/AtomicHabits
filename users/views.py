from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from users.serializers import UserSerializer


class UserCreateAPIView(CreateAPIView):
    """Создание нового пользователя"""

    serializer_class = UserSerializer
    permission_classes = [AllowAny]


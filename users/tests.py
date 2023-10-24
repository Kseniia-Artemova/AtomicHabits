import sys
from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


class UserTestCase(APITestCase):

    def setUp(self) -> None:
        super().setUp()
        self.url = reverse('users:user_registration')

    def test_user_registration_errors(self):
        data_lack_username = {
            'password': 'qwerty',
            'password2': 'qwerty'
        }
        data_wrong_username = {
            'username': 'ksu',
            'telegram_username': 'tututu',
            'password': 'qwerty',
            'password2': 'qwerty'
        }
        data_wrong_password = {
            'username': 'ksu',
            'telegram_username': '@tututu',
            'password': 'qwerty',
            'password2': 'qwertyqwerty'
        }

        response = self.client.post(self.url, data=data_lack_username)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {
            'username': ['Обязательное поле.'],
            'telegram_username': ['Обязательное поле.']
            }
        )

        response = self.client.post(self.url, data=data_wrong_username)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'telegram_username': ['Недопустимый ник Telegram.']})

        response = self.client.post(self.url, data=data_wrong_password)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'password2': ['Введенные пароли не совпадают.']})

    def test_user_registration(self):
        good_data = {
            'username': 'ksu',
            'telegram_username': '@tututu',
            'password': 'qwerty',
            'password2': 'qwerty'
        }

        response = self.client.post(self.url, data=good_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), {
            'username': 'ksu',
            'telegram_username': '@tututu'
            }
        )


class CreateSuperuserCommandTestCase(TestCase):

    def test_create_superuser(self):
        out = StringIO()
        sys.stdout = out

        call_command('create_superuser', stdout=out)
        result = out.getvalue()
        self.assertEqual(result.strip(), 'Суперпользователь создан.')

        call_command('create_superuser', stdout=out)
        result = out.getvalue().split('\n')[1]
        self.assertEqual(result.strip(), 'Суперпользователь существует.')

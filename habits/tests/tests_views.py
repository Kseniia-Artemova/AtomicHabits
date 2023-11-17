from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from habits.models import Habit, Schedule, Interval
from users.models import User


class HabitTestCase(APITestCase):

    def setUp(self) -> None:
        self.regular_user = User.objects.create(
            username='ksu',
            telegram_username='@tututu',
        )
        self.other_user = User.objects.create(
            username='other_user',
            telegram_username='@other_user',
        )
        self.superuser = User.objects.create(
            username='superuser',
            telegram_username='@superuser',
        )

        self.enjoyable_habit = Habit.objects.create(
            user=self.regular_user,
            place='дома',
            operation='отдохнуть',
            is_enjoyable=True
        )
        self.user_habit = Habit.objects.create(
            user=self.regular_user,
            place='в прыжке',
            operation='переобуться',
            is_enjoyable=False,
            reward='похлопать себе',
            lead_time='60',
            is_public=False,
            interval=Interval.objects.create(
                interval='17:00:00'
            )
        )
        self.someone_private_habit = Habit.objects.create(
            user=self.other_user,
            place='по пути',
            operation='сделать сальто',
            is_enjoyable=False,
            reward='похлопать себе',
            lead_time='60',
            is_public=False,
            schedule=Schedule.objects.create(
                monday='09:00:00',
                wednesday='09:00:00'
            )
        )
        self.someone_public_habit = Habit.objects.create(
            user=self.other_user,
            place='на работе',
            operation='поработать',
            is_enjoyable=False,
            reward='получить зарплату',
            lead_time='120',
            is_public=True,
            interval=Interval.objects.create(
                interval='02:00:00',
                start_time='10:00:00',
                end_time='18:00:00'
            )
        )

    def test_user_list_habits(self):
        self.client.force_authenticate(user=self.regular_user)

        url = reverse('habits:habits')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['results']), 2)
        self.assertEqual(response.json()['results'][0]['user'], self.regular_user.pk)

    def test_create_habit_bad_data(self):
        url = reverse('habits:habits')

        bad_data = {
            'place': 'Дома',
            'operation': 'Учить английские слова',
            'is_enjoyable': False,
            'reward': 'съесть кусочек шоколадки',
            'lead_time': '40',
        }

        response = self.client.post(url, data=bad_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user=self.regular_user)

        bad_data['schedule'] = {}
        response = self.client.post(url, data=bad_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'schedule':
                {'non_field_errors': [
                    'Должно быть указано время хотя бы для одного дня недели.'
                    ]
                }
            }
        )
        del bad_data['schedule']

        bad_data['interval'] = {'interval': '7 03:00:00'}
        response = self.client.post(url, data=bad_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'interval':
                {'interval': [
                    'Нельзя установить интервал продолжительностью больше недели'
                    ]
                }
            }
        )
        bad_data['interval'] = {'interval': '03:00:00', 'start_time': '17:00:00'}
        response = self.client.post(url, data=bad_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'interval':
                {'non_field_errors': [
                    'Либо установите и время старта, и время окончания, либо оба эти поля должны быть пусты.'
                    ]
                }
            }
        )
        del bad_data['interval']

        bad_data['lead_time'] = '160'
        response = self.client.post(url, data=bad_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'lead_time': ['Время выполнения должно быть не более 120 секунд.']})

        bad_data['lead_time'] = '120'
        response = self.client.post(url, data=bad_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'non_field_errors': [
                'Нужно выбрать что-то одно: расписание или интервал.'
                ]
            }
        )

        bad_data['is_enjoyable'] = True
        bad_data['schedule'] = {'monday': '16:00', 'wednesday': '18:00:00'}
        bad_data['related_habit'] = self.enjoyable_habit.pk
        response = self.client.post(url, data=bad_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'non_field_errors': [
                'Может быть указано только что-то одно: либо вознаграждение, либо связанная привычка.',
                'У приятной привычки не может быть своего расписания.',
                'У приятной привычки не может быть вознаграждения или связанной привычки.'
                ]
            }
        )
        del bad_data['related_habit']
        bad_data['reward'] = 'какая-то вкусняшка'
        response = self.client.post(url, data=bad_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'non_field_errors': [
                'У приятной привычки не может быть своего расписания.',
                'У приятной привычки не может быть вознаграждения или связанной привычки.'
                ]
            }
        )
        del bad_data['reward']

        bad_data['is_enjoyable'] = False
        bad_data['schedule'] = {'monday': '16:00', 'wednesday': '18:00:00'}
        bad_data['interval'] = {'interval': '03:00:00'}
        bad_data['reward'] = 'какая-то вкусняшка'
        bad_data['related_habit'] = self.someone_public_habit.pk
        response = self.client.post(url, data=bad_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'non_field_errors': [
                'Нужно выбрать что-то одно: расписание или интервал.',
                'Может быть указано только что-то одно: либо вознаграждение, либо связанная привычка.',
                'Связанная привычка должна быть приятной.'
                ]
            }
        )

    def test_create_habit_good_data(self):
        url = reverse('habits:habits')

        good_data = {
            'place': 'Дома',
            'operation': 'Учить английские слова',
            'is_enjoyable': False,
            'reward': 'съесть кусочек шоколадки',
            'lead_time': '40',
            'schedule': {'monday': '16:00', 'wednesday': '18:00:00'}
        }
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.post(url, data=good_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['place'], 'Дома')
        self.assertEqual(response.json()['user'], self.regular_user.pk)
        self.assertIsNone(response.json()['interval'])

        good_data['schedule'] = None
        good_data['interval'] = {'interval': '00:40:00', 'start_time': '10:00:00', 'end_time': '20:00:00'}
        response = self.client.post(url, data=good_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.json()['interval'])

    def test_public_list_habits(self):
        self.client.force_authenticate(user=self.regular_user)

        url = reverse('habits:public_habits')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['results']), 1)
        self.assertTrue(response.json()['results'][0]['is_public'])
        self.assertEqual(response.json()['results'][0]['user'], self.other_user.pk)

    def test_retrieve_habit(self):
        self.client.force_authenticate(user=self.regular_user)

        url = reverse('habits:user_habits', kwargs={'pk': self.someone_private_habit.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        url = reverse('habits:user_habits', kwargs={'pk': self.user_habit.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['user'], self.user_habit.user.pk)
        self.assertEqual(response.json()['reward'], self.user_habit.reward)

    def test_destroy_habit(self):
        self.client.force_authenticate(user=self.regular_user)

        url = reverse('habits:user_habits', kwargs={'pk': self.someone_private_habit.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        url = reverse('habits:user_habits', kwargs={'pk': self.user_habit.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_habit_put(self):
        self.client.force_authenticate(user=self.regular_user)

        data = {
            'place': 'в прыжке',
            'operation': 'переобуться',
            'is_enjoyable': False,
            'reward': 'похлопать себе',
            'lead_time': '60',
            'is_public': False,
            'schedule': None,
            'interval': {
                'interval': '17:00:00',
                'start_time': None,
                'end_time': None,
                'last_event': None
            },
            'related_habit': None}

        url = reverse('habits:user_habits', kwargs={'pk': self.someone_private_habit.pk})
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        url = reverse('habits:user_habits', kwargs={'pk': self.user_habit.pk})

        data['schedule'] = {'monday': '17:00:00'}
        data['interval'] = None
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.json()['interval'])
        self.assertIsNotNone(response.json()['schedule'])

        data['schedule'] = {}
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'schedule': {
                    'non_field_errors': ['Должно быть указано время хотя бы для одного дня недели.']
                    }
                }
            )

        data['schedule'] = None
        data['interval'] = {'interval': '8 06:00:00'}
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'interval': {
                'interval': ['Нельзя установить интервал продолжительностью больше недели']}
            }
        )

        data['interval'] = {'interval': '06:00:00', 'end_time': '19:00:00'}
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'interval': {
                    'non_field_errors': [
                        'Либо установите и время старта, и время окончания, либо оба эти поля должны быть пусты.'
                    ]
                }
            }
        )

        data['interval'] = {'interval': '06:00:00'}
        data['lead_time'] = '121'
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'lead_time': ['Время выполнения должно быть не более 120 секунд.']})

        data['lead_time'] = '120'
        data['is_enjoyable'] = True
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'non_field_errors': [
                'У приятной привычки не может быть своего расписания.',
                'У приятной привычки не может быть вознаграждения или связанной привычки.'
                ]
            }
        )

        data['is_enjoyable'] = False
        data['schedule'] = {'friday': '13:00:00'}
        data['related_habit'] = self.user_habit.pk
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'non_field_errors': [
                'Нужно выбрать что-то одно: расписание или интервал.',
                'Может быть указано только что-то одно: либо вознаграждение, либо связанная привычка.',
                'Связанная привычка должна быть приятной.'
                ]
            }
        )

        data['schedule'] = None
        data['related_habit'] = None
        data['is_public'] = True
        data['lead_time'] = '00:02:00'
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.json()['schedule'])
        self.assertIsNone(response.json()['related_habit'])
        self.assertTrue(response.json()['is_public'])
        self.assertEqual(response.json()['lead_time_string'], 'В течение 120 секунд')

    def test_update_habit_patch(self):
        self.client.force_authenticate(user=self.regular_user)

        data = {
            'place': 'в прыжке',
            'operation': 'переобуться',
            'is_enjoyable': False,
            'reward': 'похлопать себе',
            'lead_time': '60',
            'is_public': False,
            'schedule': None,
            'interval': {
                'interval': '17:00:00',
                'start_time': None,
                'end_time': None,
                'last_event': None
            },
            'related_habit': None}

        url = reverse('habits:user_habits', kwargs={'pk': self.someone_private_habit.pk})
        response = self.client.patch(url, data={'is_public': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        url = reverse('habits:user_habits', kwargs={'pk': self.user_habit.pk})

        response = self.client.patch(url, data={'related_habit': self.enjoyable_habit.pk}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'non_field_errors': [
                'Может быть указано только что-то одно: либо вознаграждение, либо связанная привычка.'
                ]
            }
        )

        response = self.client.patch(url, data={'is_enjoyable': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'non_field_errors': [
                'У приятной привычки не может быть вознаграждения или связанной привычки.'
                ]
            }
        )

        response = self.client.patch(url, data={'is_public': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()['is_public'])

        response = self.client.patch(url, data={'interval': {
            'start_time': '10:00:00',
            'end_time': '19:00:00'}
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['interval']['start_time'], '10:00:00')
        self.assertEqual(response.json()['interval']['end_time'], '19:00:00')

        response = self.client.patch(url, data={'schedule': {'monday': '17:00:00'}}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.json()['interval'])

        response = self.client.patch(url, data={'schedule': {'monday': '16:00:00'}}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.json()['interval'])
        self.assertEqual(response.json()['schedule']['monday'], '16:00:00')
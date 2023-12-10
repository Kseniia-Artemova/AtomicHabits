from django.test import TestCase
from habits.models import Habit, Schedule, Interval
from users.models import User


class ScheduleStrTestCase(TestCase):

    def setUp(self) -> None:
        self.schedule = Schedule.objects.create(
            monday='14:00:00',
            friday='17:00:00'
        )

    def test_str(self):
        self.assertEqual(str(self.schedule), 'пн: 14:00:00, пт: 17:00:00')


class IntervalStrTestCase(TestCase):

    def setUp(self) -> None:
        self.interval = Interval.objects.create(interval='04:00:00')

    def test_str(self):
        self.assertEqual(str(self.interval), 'Интервал продолжительностью в 04:00:00 часов')


class HabitStrTestCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(
            username='ksu',
            telegram_username='@tututu',
        )

        self.enjoyable_habit = Habit.objects.create(
            user=self.user,
            place='дома',
            operation='отдохнуть',
            is_enjoyable=True
        )
        self.user_habit = Habit.objects.create(
            user=self.user,
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
            user=self.user,
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
            user=self.user,
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

    def test_str(self):

        self.assertEqual(str(self.user_habit), 'Переобуться с интервалом в 17:00:00 часов в прыжке')
        self.assertEqual(str(self.someone_private_habit), 'Сделать сальто пн: 09:00:00, ср: 09:00:00 по пути')
        self.assertEqual(str(self.enjoyable_habit), 'Отдохнуть дома')
        self.assertEqual(str(self.someone_public_habit), 'Поработать с интервалом в 02:00:00 часов на работе')


class ServicesTestCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(
            username='ksu',
            telegram_username='@tututu',
        )

        self.habit_interval = Habit.objects.create(
            user=self.user,
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
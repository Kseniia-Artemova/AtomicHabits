from datetime import datetime

from django.test import TestCase
from django.utils import timezone

from habits import services
from habits.models import Habit, Schedule, Interval
from users.models import User


class ServicesTestCase(TestCase):

    def setUp(self) -> None:

        self.user = User.objects.create(
            username='ksu',
            telegram_username='@ksu'
        )

        self.enjoyable_habit = Habit.objects.create(
            user=self.user,
            operation='съесть авокадо',
            is_enjoyable=True
        )

        self.habit_schedule = Habit.objects.create(
            user=self.user,
            place='дома',
            operation='решать ката',
            is_enjoyable=False,
            reward='позалипать в видео',
            lead_time='00:01:00',
            schedule=Schedule.objects.create(
                monday='14:00:00',
                friday='20:00:00'
            )
        )

        self.habit_interval = Habit.objects.create(
            user=self.user,
            place='на кресле',
            operation='помедитировать',
            is_enjoyable=False,
            interval=Interval.objects.create(
                interval='03:00:00',
                start_time='10:00:00',
                end_time='19:00:00'
            ),
            related_habit=self.enjoyable_habit
        )

    def test_get_reminder_text(self):
        row_time = datetime.strptime(self.habit_schedule.schedule.monday, "%H:%M:%S").time()
        text = services.get_reminder_text(self.habit_schedule, row_time)
        expected_text = ("Напоминание! Формируем привычку, следуй указанию\n"
                         "\n"
                         "Когда: сегодня в 14:00\n"
                         "Что сделать: решать ката дома\n"
                         "В течение 00:01:00 секунд\n"
                         "В качестве поощрения: позалипать в видео\n"
                         "Успехов!")
        self.assertEqual(text, expected_text)

        row_time = timezone.now()
        text = services.get_reminder_text(self.habit_interval, row_time)
        expected_text = ("Напоминание! Формируем привычку, следуй указанию\n"
                         "\n"
                         f"Когда: сейчас, в {row_time.strftime('%H:%M')}\n"
                         "Что сделать: помедитировать на кресле\n"
                         "В качестве поощрения: Съесть авокадо\n"
                         "Успехов!")
        self.assertEqual(text, expected_text)

    def test_is_reminder_time_active(self):

        time_now = datetime.strptime("14:00:00", "%H:%M:%S").time()

        start_time = datetime.strptime("10:00:00", "%H:%M:%S").time()
        end_time = datetime.strptime("18:00:00", "%H:%M:%S").time()
        result = services.is_reminder_time_active(time_now, start_time, end_time)
        self.assertTrue(result)

        start_time = datetime.strptime("21:00:00", "%H:%M:%S").time()
        end_time = datetime.strptime("06:00:00", "%H:%M:%S").time()
        result = services.is_reminder_time_active(time_now, start_time, end_time)
        self.assertFalse(result)

        time_now = datetime.strptime("06:00:00", "%H:%M:%S").time()

        start_time = datetime.strptime("10:00:00", "%H:%M:%S").time()
        end_time = datetime.strptime("18:00:00", "%H:%M:%S").time()
        result = services.is_reminder_time_active(time_now, start_time, end_time)
        self.assertFalse(result)

        start_time = datetime.strptime("21:00:00", "%H:%M:%S").time()
        end_time = datetime.strptime("06:00:00", "%H:%M:%S").time()
        result = services.is_reminder_time_active(time_now, start_time, end_time)
        self.assertTrue(result)


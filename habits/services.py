import logging
from datetime import time

import requests
from django.utils import timezone

from config import settings
from habits.models import Habit
from users.models import User

logger = (logging.getLogger(__name__))


def send_scheduled_reminder() -> None:
    """Функция для отправки напоминаний о привычке в соответствии с недельным расписанием"""

    days_fields = [
        'monday', 'tuesday', 'wednesday',
        'thursday', 'friday', 'saturday', 'sunday'
    ]

    current_datetime = timezone.now()
    current_date = timezone.now().date()
    current_time = current_datetime.time().replace(second=0, microsecond=0)
    day_of_week = current_datetime.weekday()

    current_day_field = days_fields[day_of_week]

    habits = Habit.objects.filter(
        user__telegram_user_id__isnull=False,
        **{f'schedule__{current_day_field}__isnull': False,}
    ).exclude(schedule__last_event=current_date).select_related('user', 'schedule')

    for habit in habits:
        if getattr(habit.schedule, current_day_field).replace(second=0, microsecond=0) <= current_time:
            time_habit = getattr(habit.schedule, current_day_field)
            text = get_reminder_text(habit, time_habit)
            send_reminder(habit.user, text)
            habit.schedule.last_event = current_date
            habit.schedule.save(update_fields=['last_event'])


def send_interval_reminder() -> None:
    """Функция для отправки напоминаний о привычке с заданным интервалом"""

    current_datetime = timezone.now()
    current_time = current_datetime.time()

    habits = Habit.objects.filter(
        interval__isnull=False,
        user__telegram_user_id__isnull=False
    ).select_related('user', 'interval')

    for habit in habits:
        start_time = habit.interval.start_time
        end_time = habit.interval.end_time
        if not is_reminder_time_active(current_time, start_time, end_time):
            continue
        if habit.interval.last_event and (habit.interval.last_event + habit.interval.interval) > current_datetime:
            continue
        text = get_reminder_text(habit, current_time)
        send_reminder(habit.user, text)
        habit.interval.last_event = current_datetime
        habit.interval.save(update_fields=['last_event'])
        continue


def is_reminder_time_active(current_time: time, start_time: time, end_time: time) -> bool:
    """
    Вспомогательная функция проверки активности рассылки в зависимости от времени
    (пользователь может задать временной промежуток активности рассылки)
    """

    if start_time and end_time:
        if start_time < end_time and not (start_time <= current_time < end_time):
            return False
        if start_time > end_time and not (current_time >= start_time or current_time <= end_time):
            return False
    return True


def send_reminder(user: User, text: str) -> None:
    """Вспомогательная функция отправки пользователю напоминания о привычке через telegram"""

    params = {
        'chat_id': user.telegram_user_id,
        'text': text
    }
    url = settings.TELEGRAM_MAIN_URL + settings.TELEGRAM_TOKEN + '/sendMessage'
    try:
        response = requests.post(url, params=params, timeout=10)
        response.raise_for_status()
        logger.info(f"Сообщение отправлено {user.telegram_username}. Ответ: {response.json()}")
    except requests.RequestException as e:
        logger.error(f"Ошибка при отправке сообщения пользователю {user.telegram_username}. Ошибка: {e}")


def get_reminder_text(habit: Habit, row_time: time) -> str:
    """Возвращает готовый текст напоминания о привычке для отправки пользователям"""

    place = habit.place if habit.place else ''
    lead_time = f'В течение {habit.lead_time} секунд\n' if habit.lead_time else ''
    reward = f'В качестве поощрения: {habit.reward or habit.related_habit}\n' if habit.reward or habit.related_habit else ''
    formatted_time = row_time.strftime('%H:%M')
    time_habit = ''
    if habit.schedule:
        time_habit = f'Когда: сегодня в {formatted_time}'
    elif habit.interval:
        time_habit = f'Когда: сейчас, в {formatted_time}'

    text = (f'Напоминание! Формируем привычку, следуй указанию\n'
            f'\n'
            f'{time_habit}\n'
            f'Что сделать: {habit.operation} {place}\n'
            f'{lead_time}'
            f'{reward}'
            f'Успехов!')

    return text

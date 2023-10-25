from datetime import timedelta

from django.db import models

from users.models import User


NULLABLE = {'null': True, 'blank': True}


class Schedule(models.Model):
    """Расписание для привычки по дням недели"""

    monday = models.TimeField(**NULLABLE, verbose_name='Понедельник, время выполнения')
    tuesday = models.TimeField(**NULLABLE, verbose_name='Вторник, время выполнения')
    wednesday = models.TimeField(**NULLABLE, verbose_name='Среда, время выполнения')
    thursday = models.TimeField(**NULLABLE, verbose_name='Четверг, время выполнения')
    friday = models.TimeField(**NULLABLE, verbose_name='Пятница, время выполнения')
    saturday = models.TimeField(**NULLABLE, verbose_name='Суббота, время выполнения')
    sunday = models.TimeField(**NULLABLE, verbose_name='Воскресенье, время выполнения')

    last_event = models.DateField(**NULLABLE, verbose_name='Дата последней отправки напоминания')

    def __str__(self):
        days_of_week = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']
        schedule = []
        i = -1
        for field in self._meta.fields:
            if isinstance(field, models.TimeField):
                value = getattr(self, field.name)
                i += 1
                if value:
                    schedule.append(f'{days_of_week[i]}: {value}')

        return ', '.join(schedule)

    class Meta:
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписания'


class Interval(models.Model):
    """Интервал между напоминаниями о привычке"""

    interval = models.DurationField(verbose_name='Интервал между напоминаниями, часы')
    start_time = models.TimeField(**NULLABLE, verbose_name='Время старта')
    end_time = models.TimeField(**NULLABLE, verbose_name='Время окончания')
    last_event = models.DateTimeField(**NULLABLE, verbose_name='Время последнего напоминания')

    def __str__(self):
        return f'Интервал продолжительностью в {self.interval} часов'

    class Meta:
        verbose_name = 'Интервал'
        verbose_name_plural = 'Интервалы'


class Habit(models.Model):
    """
    Привычка.

    Можно выбрать либо расписание по дням недели, либо интервал между напоминаниями о привычке (выражен в часах)
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')

    place = models.CharField(max_length=200, **NULLABLE, verbose_name='Где')
    operation = models.CharField(max_length=200, verbose_name='Действие')
    is_enjoyable = models.BooleanField(default=False, verbose_name='Приятная привычка')

    reward = models.CharField(max_length=100, **NULLABLE, verbose_name='Вознаграждение')
    lead_time = models.DurationField(**NULLABLE, verbose_name='Продолжительность выполнения, секунды')
    is_public = models.BooleanField(default=False, verbose_name='Публичная')

    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, **NULLABLE, verbose_name='Расписание')
    interval = models.ForeignKey(Interval, on_delete=models.CASCADE, **NULLABLE, verbose_name='Интервал')
    related_habit = models.ForeignKey('Habit',
                                      **NULLABLE,
                                      on_delete=models.SET_NULL,
                                      verbose_name='Связанная привычка')

    def __str__(self):
        primary_text = f'{self.operation}'
        place = f' {self.place}' if self.place else ''
        if self.interval:
            interval_text = f'с интервалом в {self.interval.interval} часов'
            return (primary_text + ' ' + interval_text + place).capitalize()
        elif self.schedule:
            return (primary_text + ' ' + str(self.schedule) + place).capitalize()
        else:
            return (primary_text + place).capitalize()

    class Meta:
        verbose_name = 'Привычка'
        verbose_name_plural = 'Привычки'
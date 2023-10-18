from datetime import timedelta

from django.db import transaction
from rest_framework import serializers

from habits.models import Habit, Schedule, Interval


class ScheduleSerializer(serializers.ModelSerializer):
    """Сериализатор для описания расписания по дням недели"""

    class Meta:
        model = Schedule
        fields = '__all__'

    def validate(self, attrs):
        if not any(attrs.values()):
            raise serializers.ValidationError('Должно быть указано время хотя бы для одного дня недели.')


class IntervalSerializer(serializers.ModelSerializer):
    """Сериализатор для описания интервала между напоминаниями"""

    class Meta:
        model = Interval
        fields = '__all__'

    def validate(self, attrs):
        if bool(attrs.get('start_time')) != bool(attrs.get('end_time')):
            raise serializers.ValidationError(
                'Либо установите и время старта, и время окончания, либо оба эти поля должны быть пусты.'
            )

    def validate_interval(self, value):
        HOURS_IN_DAY = 24
        DAYS_IN_WEEK = 7

        if type(value) is not int or value <= 0:
            raise serializers.ValidationError(
                'Интервал должен быть выражен целым числом, равным нужному количеству часов.'
            )

        if value > HOURS_IN_DAY * DAYS_IN_WEEK:
            raise serializers.ValidationError('Нельзя установить интервал продолжительностью больше недели')
        return timedelta(hours=value)


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор для обработки данных о привычке"""

    schedule = ScheduleSerializer()
    interval = IntervalSerializer()

    class Meta:
        model = Habit
        read_only_fields = ('user', )

    def validate(self, attrs):
        errors = []

        if attrs.get('lead_time') and attrs.get('lead_time').seconds > 120:
            errors.append('Время выполнения должно быть не более 120 секунд.')

        if attrs.get('is_enjoyable'):
            if attrs.get('schedule') or attrs.get('interval'):
                errors.append('У приятной привычки не может быть своего расписания.')
            if attrs.get('reward') or attrs.get('related_habit'):
                errors.append(
                    'У приятной привычки не может быть вознаграждения или связанной привычки.'
                )
        else:
            if bool(attrs.get('schedule')) == bool(attrs.get('interval')):
                errors.append('Нужно выбрать что-то одно: расписание или интервал.')
            if attrs.get('related_habit') and attrs.get('reward'):
                errors.append(
                    'Может быть указано только что-то одно: либо вознаграждение, либо связанная привычка.'
                )
            if attrs.get('related_habit') and not attrs.get('related_habit').is_enjoyable:
                errors.append('Связанная привычка должна быть приятной.')

        if errors:
            raise serializers.ValidationError(errors)
        
        return super().validate(attrs)

    @transaction.atomic
    def create(self, validated_data):
        schedule_data = validated_data.pop('schedule', None)
        interval_data = validated_data.pop('interval', None)

        if schedule_data is not None:
            validated_data['schedule'] = Schedule.objects.create(**schedule_data)

        if interval_data is not None:
            validated_data['interval'] = Interval.objects.create(**interval_data)

        return super().create(validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        schedule_data = validated_data.pop('schedule', None)
        interval_data = validated_data.pop('interval', None)

        if self.context['request'].method == 'PUT' and not (schedule_data or interval_data):
            if instance.schedule:
                instance.schedule.delete()
            if instance.interval:
                instance.interval.delete()

        if schedule_data is not None:
            if instance.schedule:
                for key, value in schedule_data.items():
                    setattr(instance.schedule, key, value)
                instance.schedule.save()
            elif instance.interval:
                instance.interval.delete()
                instance.schedule = Schedule.objects.create(**schedule_data)

        if interval_data is not None:
            if instance.interval:
                for key, value in interval_data.items():
                    setattr(instance.interval, key, value)
                instance.interval.save()
            elif instance.schedule:
                instance.schedule.delete()
                instance.interval = Interval.objects.create(**interval_data)

        return super().update(instance, validated_data)

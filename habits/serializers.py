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
        return super().validate(attrs)


class IntervalSerializer(serializers.ModelSerializer):
    """Сериализатор для описания интервала между напоминаниями"""

    interval_string = serializers.SerializerMethodField('get_interval_string')

    class Meta:
        model = Interval
        fields = ('id', 'interval_string', 'start_time', 'end_time', 'is_active', 'last_event', 'interval')
        extra_kwargs = {
            'interval': {'write_only': True},
            'interval_string': {'read_only': True},
            'is_active': {'read_only': True},
            'last_event': {'read_only': True},
        }

    def validate(self, attrs):
        if bool(attrs.get('start_time')) != bool(attrs.get('end_time')):
            raise serializers.ValidationError(
                'Либо установите и время старта, и время окончания, либо оба эти поля должны быть пусты.'
            )
        return super().validate(attrs)

    def validate_interval(self, value):
        DAYS_IN_WEEK = 7

        if value > timedelta(days=DAYS_IN_WEEK):
            raise serializers.ValidationError('Нельзя установить интервал продолжительностью больше недели')
        return super().validate(value)

    def get_interval_string(self, obj):
        total_seconds = round(obj.interval.total_seconds())
        return f'Через каждые {total_seconds // 3600} часов'


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор для обработки данных о привычке"""

    schedule = ScheduleSerializer(required=False, allow_null=True)
    interval = IntervalSerializer(required=False, allow_null=True)
    lead_time_string = serializers.SerializerMethodField()

    class Meta:
        model = Habit
        fields = ('user', 'place', 'operation', 'is_enjoyable', 'reward', 'lead_time', 'lead_time_string',
                  'is_public', 'schedule', 'interval', 'related_habit')
        extra_kwargs = {
            'lead_time': {'write_only': True},
            'lead_time_string': {'read_only': True},
            'user': {'read_only': True}
        }

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

        if self.context['request'].method == 'PUT':
            if instance.schedule:
                instance.schedule.delete()
                instance.schedule = None
            if instance.interval:
                instance.interval.delete()
                instance.interval = None

        if schedule_data:
            if instance.schedule:
                for key, value in schedule_data.items():
                    setattr(instance.schedule, key, value)
                instance.schedule.save()
            else:
                instance.schedule = Schedule.objects.create(**schedule_data)
                if instance.interval:
                    instance.interval.delete()

        if interval_data:
            if instance.interval:
                for key, value in interval_data.items():
                    setattr(instance.interval, key, value)
                instance.interval.save()
            else:
                instance.interval = Interval.objects.create(**interval_data)
                if instance.schedule:
                    instance.schedule.delete()

        instance.save()

        return super().update(instance, validated_data)

    def get_lead_time_string(self, obj):
        seconds = round(obj.lead_time.total_seconds())
        return f'В течение {seconds} секунд'




from django.contrib import admin

from habits.models import Habit, Schedule, Interval


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'place', 'operation', 'is_enjoyable', 'reward',
                    'lead_time', 'is_public', 'schedule', 'interval', 'related_habit')


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('id', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')


@admin.register(Interval)
class IntervalAdmin(admin.ModelAdmin):
    list_display = ('id', 'interval', 'start_time', 'end_time', 'last_event')
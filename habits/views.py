from django.shortcuts import render
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from habits.models import Habit
from habits.pagination import FiveObjectsPagination
from habits.permissions import OnlyOwnerOrSuperuser
from habits.serializers import HabitSerializer


class UserHabitListAPIView(ListAPIView):
    """Представление для отображения списка привычек, принадлежащих текущему пользователю"""

    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = FiveObjectsPagination

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user).select_related('schedule', 'interval', 'related_habit')


class PublicHabitListAPIView(ListAPIView):
    """Представление для отображения списка всех публичных привычек"""

    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = FiveObjectsPagination

    def get_queryset(self):
        return Habit.objects.filter(is_public=True).select_related('schedule', 'interval', 'related_habit')


class HabitCreateAPIView(CreateAPIView):
    """Представление для создания привычки"""

    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class HabitRetrieveAPIView(RetrieveAPIView):
    """Представление для просмотра привычки"""

    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, OnlyOwnerOrSuperuser]
    queryset = Habit.objects.all()


class HabitUpdateAPIView(UpdateAPIView):
    """Представление для редактирования привычки"""

    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, OnlyOwnerOrSuperuser]
    queryset = Habit.objects.all().select_related('interval', 'schedule')


class HabitDestroyAPIView(DestroyAPIView):
    """Представление для удаления привычки"""

    permission_classes = [IsAuthenticated, OnlyOwnerOrSuperuser]
    queryset = Habit.objects.all()


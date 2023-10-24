from django.shortcuts import render
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView, RetrieveAPIView, \
    RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from habits.models import Habit
from habits.pagination import FiveObjectsPagination
from habits.permissions import OnlyOwnerOrSuperuser
from habits.serializers import HabitSerializer


class PublicHabitListAPIView(ListAPIView):
    """Представление для отображения списка всех публичных привычек"""

    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = FiveObjectsPagination

    def get_queryset(self):
        return Habit.objects.filter(is_public=True).select_related('schedule', 'interval', 'related_habit')


# class UserHabitListAPIView(ListAPIView):
#     """Представление для отображения списка привычек, принадлежащих текущему пользователю"""
#
#     serializer_class = HabitSerializer
#     permission_classes = [IsAuthenticated]
#     pagination_class = FiveObjectsPagination
#
#     def get_queryset(self):
#         return Habit.objects.filter(user=self.request.user).select_related('schedule', 'interval', 'related_habit')
#
#
# class HabitCreateAPIView(CreateAPIView):
#     """Представление для создания привычки"""
#
#     serializer_class = HabitSerializer
#     permission_classes = [IsAuthenticated]
#
#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)
#
#
# class HabitRetrieveAPIView(RetrieveAPIView):
#     """Представление для просмотра привычки"""
#
#     serializer_class = HabitSerializer
#     permission_classes = [IsAuthenticated, OnlyOwnerOrSuperuser]
#     queryset = Habit.objects.all()
#
#
# class HabitUpdateAPIView(UpdateAPIView):
#     """Представление для редактирования привычки"""
#
#     serializer_class = HabitSerializer
#     permission_classes = [IsAuthenticated, OnlyOwnerOrSuperuser]
#     queryset = Habit.objects.all().select_related('interval', 'schedule', 'related_habit')
#
#
# class HabitDestroyAPIView(DestroyAPIView):
#     """Представление для удаления привычки"""
#
#     permission_classes = [IsAuthenticated, OnlyOwnerOrSuperuser]
#     queryset = Habit.objects.all()


# Мультидженерики
# Преимущество в одном url на них, с разницей наличии/отсутствии id
# Это более правильный способ работы с REST
class HabitRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """
    Представление для отображения привычек,
    обрабатывает методы 'GET', 'DELETE', 'PUT', 'PATCH'
    Доступ только для владельца или суперюзера
    """

    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, OnlyOwnerOrSuperuser]

    def get_queryset(self):
        if self.request.method == 'DELETE':
            return Habit.objects.all()
        elif self.request.method in ('GET', 'PUT', 'PATCH'):
            return Habit.objects.all().select_related('schedule', 'interval', 'related_habit')


class HabitListCreateAPIView(ListCreateAPIView):
    """
    Представление для отображения привычек,
    обрабатывает методы 'GET', 'POST'
    Доступ только для владельца или суперюзера
    """

    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = FiveObjectsPagination

    def get_queryset(self):
        if self.request.method == 'GET':
            return Habit.objects.filter(user=self.request.user).select_related('schedule', 'interval', 'related_habit')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



from django.urls import path

from habits.apps import HabitsConfig
from habits.views import PublicHabitListAPIView, HabitRetrieveUpdateDestroyAPIView, HabitListCreateAPIView

app_name = HabitsConfig.name

urlpatterns = [
    path('<int:pk>/', HabitRetrieveUpdateDestroyAPIView.as_view(), name='user_habits'),
    path('', HabitListCreateAPIView.as_view(), name='habits'),
    path('public/', PublicHabitListAPIView.as_view(), name='public_habits'),
]
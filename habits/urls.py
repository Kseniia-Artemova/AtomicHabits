from django.urls import path

from habits.views import UserHabitListAPIView, PublicHabitListAPIView, HabitCreateAPIView, HabitUpdateAPIView, \
    HabitDestroyAPIView

urlpatterns = [
    path('user_habits/', UserHabitListAPIView.as_view(), name='user_habits'),
    path('public_habits/', PublicHabitListAPIView.as_view(), name='public_habits'),
    path('create/', HabitCreateAPIView.as_view(), name='create_habit'),
    path('<int:pk>/update/', HabitUpdateAPIView.as_view(), name='update_habit'),
    path('<int:pk>/delete/', HabitDestroyAPIView.as_view(), name='delete_habit'),
]
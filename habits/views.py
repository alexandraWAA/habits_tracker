from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from habits.models import Habit
from habits.serializers import HabitSerializer, HabitCreateUpdateSerializer, PublicHabitSerializer
from habits.permissions import IsOwner, IsOwnerOrReadOnly
from habits.pagination import HabitPagination


class HabitListCreateView(generics.ListCreateAPIView):
    """
    Список привычек пользователя и создание новой
    """
    serializer_class = HabitSerializer
    pagination_class = HabitPagination

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return HabitCreateUpdateSerializer
        return HabitSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class HabitRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    Получение, обновление и удаление привычки
    """
    queryset = Habit.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return HabitCreateUpdateSerializer
        return HabitSerializer


class PublicHabitListView(generics.ListAPIView):
    """
    Список публичных привычек (доступен всем авторизованным пользователям)
    """
    serializer_class = PublicHabitSerializer
    pagination_class = HabitPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Habit.objects.filter(is_public=True)
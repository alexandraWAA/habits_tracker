from rest_framework import serializers
from habits.models import Habit


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор для привычек"""
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Habit
        fields = [
            'id', 'user', 'user_email', 'place', 'time', 'action',
            'is_pleasant', 'related_habit', 'periodicity', 'reward',
            'execution_time', 'is_public', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']


class HabitCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/обновления привычек"""
    class Meta:
        model = Habit
        fields = [
            'place', 'time', 'action', 'is_pleasant', 'related_habit',
            'periodicity', 'reward', 'execution_time', 'is_public'
        ]

    def validate_periodicity(self, value):
        if value < 1 or value > 7:
            raise serializers.ValidationError('Периодичность должна быть от 1 до 7 дней')
        return value

    def validate_execution_time(self, value):
        if value > 120:
            raise serializers.ValidationError('Время выполнения не может превышать 120 секунд')
        return value


class PublicHabitSerializer(serializers.ModelSerializer):
    """Сериализатор для публичных привычек (только чтение)"""
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Habit
        fields = [
            'id', 'user_email', 'place', 'time', 'action',
            'periodicity', 'execution_time', 'created_at'
        ]
        read_only_fields = '__all__'
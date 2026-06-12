from django.core.exceptions import ValidationError


def validate_no_reward_and_related_habit(habit):
    """Исключить одновременный выбор связанной привычки и указания вознаграждения"""
    if habit.reward and habit.related_habit:
        raise ValidationError('Нельзя одновременно указывать вознаграждение и связанную привычку')


def validate_related_habit_is_pleasant(habit):
    """В связанные привычки могут попадать только привычки с признаком приятной привычки"""
    if habit.related_habit and not habit.related_habit.is_pleasant:
        raise ValidationError('Связанная привычка должна быть приятной')


def validate_pleasant_habit_no_reward_or_related(habit):
    """У приятной привычки не может быть вознаграждения или связанной привычки"""
    if habit.is_pleasant and (habit.reward or habit.related_habit):
        raise ValidationError('У приятной привычки не может быть вознаграждения или связанной привычки')


def validate_execution_time(habit):
    """Время выполнения должно быть не больше 120 секунд"""
    if habit.execution_time > 120:
        raise ValidationError('Время выполнения не может превышать 120 секунд')


def validate_periodicity(habit):
    """Периодичность должна быть от 1 до 7 дней"""
    if habit.periodicity < 1 or habit.periodicity > 7:
        raise ValidationError('Периодичность должна быть от 1 до 7 дней')
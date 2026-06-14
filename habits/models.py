from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from habits.validators import (
    validate_no_reward_and_related_habit,
    validate_related_habit_is_pleasant,
    validate_pleasant_habit_no_reward_or_related,
    validate_execution_time,
    validate_periodicity
)


class Habit(models.Model):
    """
    Модель привычки
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='habits',
        verbose_name='Пользователь'
    )
    place = models.CharField(max_length=200, verbose_name='Место', help_text='Где выполнять привычку')
    time = models.TimeField(verbose_name='Время', help_text='Когда выполнять привычку')
    action = models.CharField(max_length=200, verbose_name='Действие', help_text='Что делать')
    is_pleasant = models.BooleanField(default=False, verbose_name='Приятная привычка')
    related_habit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_to',
        verbose_name='Связанная привычка',
        help_text='Привычка, которая связана с этой'
    )
    periodicity = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(7)],
        verbose_name='Периодичность (дни)',
        help_text='Как часто выполнять привычку (1-7 дней)'
    )
    reward = models.CharField(max_length=200, blank=True, null=True, verbose_name='Вознаграждение')
    execution_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(120)],
        verbose_name='Время на выполнение (секунды)',
        help_text='Не более 120 секунд'
    )
    is_public = models.BooleanField(default=False, verbose_name='Публичная привычка')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Привычка'
        verbose_name_plural = 'Привычки'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email}: {self.action} в {self.time} в {self.place}"

    def clean(self):
        validate_no_reward_and_related_habit(self)
        validate_related_habit_is_pleasant(self)
        validate_pleasant_habit_no_reward_or_related(self)
        validate_execution_time(self)
        validate_periodicity(self)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from celery import shared_task
from celery.utils.log import get_task_logger
from habits.models import Habit
from habits.services import send_telegram_notification

logger = get_task_logger(__name__)


@shared_task
def send_habit_notifications():
    """
    Отправка уведомлений о привычках, которые нужно выполнить
    """
    now = timezone.now()
    current_time = now.time()
    current_weekday = now.weekday() + 1  # ПН=1, ВС=7

    # Ищем привычки, которые нужно выполнить в текущее время
    # Учитываем периодичность (допустим, что привычка выполняется в определенные дни)
    habits = Habit.objects.filter(
        time__gte=current_time,
        time__lte=(datetime.min + timedelta(minutes=5)).time(),
        user__telegram_chat_id__isnull=False
    )

    for habit in habits:
        # Проверяем, нужно ли выполнять привычку сегодня
        # Упрощенная логика: если периодичность = 1, то каждый день
        # TODO: добавить более сложную логику с днями недели
        send_telegram_notification.delay(habit.id)


@shared_task
def send_telegram_notification(habit_id):
    """
    Отправка уведомления в Telegram
    """
    import requests
    from django.conf import settings

    try:
        habit = Habit.objects.select_related('user').get(pk=habit_id)
    except Habit.DoesNotExist:
        logger.error('Привычка %d не найдена', habit_id)
        return

    chat_id = habit.user.telegram_chat_id
    if not chat_id:
        logger.warning('У пользователя %s нет chat_id', habit.user.email)
        return

    message = (
        f"🔔 Напоминание о привычке!\n\n"
        f"📍 Место: {habit.place}\n"
        f"⏰ Время: {habit.time.strftime('%H:%M')}\n"
        f"🎯 Действие: {habit.action}\n"
        f"⏱ Время выполнения: {habit.execution_time} сек."
    )

    if habit.reward:
        message += f"\n🎁 Вознаграждение: {habit.reward}"
    elif habit.related_habit:
        message += f"\n🔗 Связанная привычка: {habit.related_habit.action}"

    url = f"{settings.TELEGRAM_BOT_URL}{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }

    try:
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            logger.info('Уведомление отправлено пользователю %s', habit.user.email)
        else:
            logger.error('Ошибка отправки: %s', response.text)
    except Exception as e:
        logger.error('Ошибка при отправке запроса: %s', e)
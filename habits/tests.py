from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from users.models import User
from habits.models import Habit


class HabitTests(APITestCase):
    """Тесты для привычек"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@test.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        self.habit_data = {
            'place': 'Дом',
            'time': '08:00:00',
            'action': 'Сделать зарядку',
            'execution_time': 60,
            'periodicity': 1
        }

    def test_create_habit_success(self):
        """Тест успешного создания привычки"""
        url = reverse('habit-list-create')
        response = self.client.post(url, self.habit_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 1)
        self.assertEqual(Habit.objects.first().action, 'Сделать зарядку')

    def test_create_habit_execution_time_too_long(self):
        """Тест: время выполнения не может быть больше 120 секунд"""
        data = self.habit_data.copy()
        data['execution_time'] = 150

        url = reverse('habit-list-create')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('execution_time', response.data)

    def test_create_habit_periodicity_invalid(self):
        """Тест: периодичность должна быть от 1 до 7"""
        data = self.habit_data.copy()
        data['periodicity'] = 10

        url = reverse('habit-list-create')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('periodicity', response.data)

    def test_create_habit_with_reward_and_related_habit_forbidden(self):
        """Тест: нельзя одновременно указывать вознаграждение и связанную привычку"""
        pleasant_habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            time='09:00:00',
            action='Отдохнуть',
            is_pleasant=True,
            execution_time=30
        )

        data = self.habit_data.copy()
        data['reward'] = 'Шоколадка'
        data['related_habit'] = pleasant_habit.id

        url = reverse('habit-list-create')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_habit_with_non_pleasant_related_habit_forbidden(self):
        """Тест: связанная привычка должна быть приятной"""
        non_pleasant = Habit.objects.create(
            user=self.user,
            place='Дом',
            time='09:00:00',
            action='Учиться',
            is_pleasant=False,
            execution_time=30
        )

        data = self.habit_data.copy()
        data['related_habit'] = non_pleasant.id

        url = reverse('habit-list-create')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_pleasant_habit_with_reward_forbidden(self):
        """Тест: у приятной привычки не может быть вознаграждения"""
        data = self.habit_data.copy()
        data['is_pleasant'] = True
        data['reward'] = 'Шоколадка'

        url = reverse('habit-list-create')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_user_habits(self):
        """Тест: список привычек пользователя"""
        Habit.objects.create(
            user=self.user,
            place='Дом',
            time='08:00:00',
            action='Зарядка',
            execution_time=60
        )
        Habit.objects.create(
            user=self.user,
            place='Офис',
            time='12:00:00',
            action='Прогулка',
            execution_time=30
        )

        url = reverse('habit-list-create')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_user_cannot_see_others_habits(self):
        """Тест: пользователь не видит чужие привычки"""
        other_user = User.objects.create_user(
            email='other@test.com',
            password='otherpass123'
        )
        Habit.objects.create(
            user=other_user,
            place='Дом',
            time='08:00:00',
            action='Чужая привычка',
            execution_time=60
        )

        url = reverse('habit-list-create')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_user_can_update_own_habit(self):
        """Тест: пользователь может обновить свою привычку"""
        habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            time='08:00:00',
            action='Зарядка',
            execution_time=60
        )

        url = reverse('habit-detail', args=[habit.id])
        response = self.client.patch(url, {'action': 'Утренняя зарядка'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['action'], 'Утренняя зарядка')

    def test_user_cannot_update_others_habit(self):
        """Тест: пользователь не может обновить чужую привычку"""
        other_user = User.objects.create_user(
            email='other@test.com',
            password='otherpass123'
        )
        habit = Habit.objects.create(
            user=other_user,
            place='Дом',
            time='08:00:00',
            action='Чужая привычка',
            execution_time=60
        )

        url = reverse('habit-detail', args=[habit.id])
        response = self.client.patch(url, {'action': 'Попытка обновить'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_delete_own_habit(self):
        """Тест: пользователь может удалить свою привычку"""
        habit = Habit.objects.create(
            user=self.user,
            place='Дом',
            time='08:00:00',
            action='Зарядка',
            execution_time=60
        )

        url = reverse('habit-detail', args=[habit.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.count(), 0)

    def test_public_habits_list(self):
        """Тест: список публичных привычек"""
        Habit.objects.create(
            user=self.user,
            place='Дом',
            time='08:00:00',
            action='Публичная привычка',
            execution_time=60,
            is_public=True
        )
        Habit.objects.create(
            user=self.user,
            place='Офис',
            time='12:00:00',
            action='Приватная привычка',
            execution_time=30,
            is_public=False
        )

        url = reverse('public-habits')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['action'], 'Публичная привычка')


class RegistrationTests(APITestCase):
    """Тесты для регистрации пользователей"""

    def test_register_user_success(self):
        """Тест успешной регистрации"""
        url = reverse('register')
        data = {
            'email': 'newuser@test.com',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='newuser@test.com').exists())

    def test_register_user_duplicate_email(self):
        """Тест: нельзя зарегистрироваться с существующим email"""
        User.objects.create_user(email='existing@test.com', password='pass123')

        url = reverse('register')
        data = {
            'email': 'existing@test.com',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
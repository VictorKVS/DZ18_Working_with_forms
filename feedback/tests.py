"""
FILE: tests.py
PATH: feedback/tests.py
PURPOSE:
    Комплексное тестирование приложения feedback.
    
RESPONSIBILITY:
    - Проверка бизнес-логики (MessageService)
    - Проверка запросов (selectors)
    - Проверка HTTP и AJAX интеграции (views)
    - Обеспечение Fail-fast валидации

ARCHITECTURAL GUARANTEES:
    - Тесты изолированы (используется TestCase с транзакционной БД)
    - Проверка как успешных сценариев (Happy Path), так и ошибок (Negative Path)
    -Datetime-сравнения используют delta для избежания flaky-тестов
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from feedback.models import Message
from feedback.services import MessageService
from feedback.selectors import get_messages_by_user_email, get_replies_for_message


class MessageServiceTests(TestCase):
    """
    Unit-тесты для слоя бизнес-логики (MessageService).
    """

    def setUp(self):
        """Arrange: Подготовка тестовых данных."""
        self.valid_data = {
            'name': 'Иван Иванов',
            'email': 'ivan@example.com',
            'text': 'Тестовое сообщение'
        }

    def test_send_message_creates_root_message_with_deadline(self):
        """Act/Assert: Корневое сообщение создается с дедлайном +24 часа."""
        message = MessageService.send_message(**self.valid_data)
        
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(message.name, 'Иван Иванов')
        self.assertFalse(message.is_read)
        self.assertIsNotNone(message.response_deadline)
        
        # Проверка дедлайна с допуском в 5 секунд (избегаем flaky-тестов)
        expected_deadline = timezone.now() + timedelta(hours=24)
        self.assertAlmostEqual(
            message.response_deadline, 
            expected_deadline, 
            delta=timedelta(seconds=5)
        )

    def test_send_message_creates_reply_without_auto_deadline(self):
        """Act/Assert: Ответ на сообщение не получает автоматический дедлайн."""
        parent = MessageService.send_message(**self.valid_data)
        reply_data = {
            'name': 'Администратор',
            'email': 'admin@example.com',
            'text': 'Ответ на сообщение',
            'parent_message': parent
        }
        
        reply = MessageService.send_message(**reply_data)
        
        self.assertEqual(Message.objects.count(), 2)
        self.assertEqual(reply.parent_message, parent)
        self.assertIsNone(reply.response_deadline)

    def test_mark_as_read_updates_status(self):
        """Act/Assert: Метод mark_as_read корректно меняет статус."""
        message = MessageService.send_message(**self.valid_data)
        self.assertFalse(message.is_read)
        
        updated_message = MessageService.mark_as_read(message.id)
        
        self.assertTrue(updated_message.is_read)
        # Проверяем, что в БД тоже обновилось
        self.assertTrue(Message.objects.get(id=message.id).is_read)


class MessageSelectorsTests(TestCase):
    """
    Unit-тесты для слоя запросов (selectors).
    """

    def setUp(self):
        self.email = 'test@example.com'
        self.msg1 = Message.objects.create(name='User', email=self.email, text='Msg 1')
        self.msg2 = Message.objects.create(name='User', email=self.email, text='Msg 2')
        self.msg3 = Message.objects.create(name='Other', email='other@example.com', text='Msg 3')
        
        # Создаем ответ на msg1
        self.reply1 = Message.objects.create(
            name='Admin', email='admin@example.com', text='Reply 1', parent_message=self.msg1
        )

    def test_get_messages_by_user_email_returns_correct_count(self):
        """Act/Assert: Селектор возвращает только сообщения указанного пользователя."""
        messages = get_messages_by_user_email(self.email)
        
        self.assertEqual(messages.count(), 2)
        self.assertIn(self.msg1, messages)
        self.assertIn(self.msg2, messages)
        self.assertNotIn(self.msg3, messages)

    def test_get_replies_for_message_returns_only_children(self):
        """Act/Assert: Селектор возвращает только дочерние сообщения."""
        replies = get_replies_for_message(self.msg1.id)
        
        self.assertEqual(replies.count(), 1)
        self.assertEqual(replies.first(), self.reply1)


class FeedbackViewsTests(TestCase):
    """
    Integration-тесты для HTTP-обёрток (views).
    """

    def setUp(self):
        self.client = Client()
        self.url = reverse('feedback:send_message')
        self.valid_payload = {
            'name': 'Пётр Петров',
            'email': 'petr@example.com',
            'text': 'Сообщение из теста view'
        }

    def test_send_message_view_http_success(self):
        """Act/Assert: Обычный POST-запрос перенаправляет и показывает успех."""
        response = self.client.post(self.url, self.valid_payload)
        
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertEqual(Message.objects.count(), 1)
        
        # Проверка сообщения в сессии (django.contrib.messages)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertIn('успешно отправлено', str(messages[0]))

    def test_send_message_view_ajax_success(self):
        """Act/Assert: AJAX POST-запрос возвращает JSON со статусом success."""
        response = self.client.post(
            self.url, 
            self.valid_payload,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(Message.objects.count(), 1)

    def test_send_message_view_ajax_validation_error(self):
        """Negative Test: AJAX POST с невалидными данными возвращает 400 и ошибки."""
        invalid_payload = {
            'name': 'Имя',
            'email': 'invalid-email',  # Ошибка валидации EmailField
            'text': 'Текст'
        }
        
        response = self.client.post(
            self.url, 
            invalid_payload,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertIn('errors', data)
        self.assertIn('email', data['errors'])  # Проверяем, что ошибка именно в поле email

    def test_message_detail_view_marks_as_read(self):
        """Act/Assert: Просмотр деталей сообщения автоматически помечает его как прочитанное."""
        message = MessageService.send_message(
            name='Test', email='test@test.com', text='Detail test'
        )
        self.assertFalse(message.is_read)
        
        url = reverse('feedback:message_detail', kwargs={'message_id': message.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Проверяем, что в БД статус изменился
        message.refresh_from_db()
        self.assertTrue(message.is_read)
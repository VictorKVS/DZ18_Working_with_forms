"""
FILE: services.py
PATH: feedback/services.py
PURPOSE:
    Бизнес-логика для работы с сообщениями и перепиской.

RESPONSIBILITY:
    - Создание новых сообщений
    - Создание ответов на сообщения
    - Пометка сообщений как прочитанных
    - Установка дедлайнов ответов
    - Проверка просроченных сообщений

INPUT DATA:
    - name: str
    - email: str
    - text: str
    - parent_message: Message | None
    - response_deadline: datetime | None

OUTPUT DATA:
    - Message instance (created/saved)

UPSTREAM:
    - feedback/views.py (HTTP handlers)

DOWNSTREAM:
    - feedback/models.py (DB operations)
    - feedback/selectors.py (read operations)

DATA FLOW:
    View → Service → Model → DB

ARCHITECTURAL GUARANTEES:
    - Все операции атомарные (transaction.atomic)
    - Валидация входных данных
    - Обработка ошибок через исключения
    - Автоматическая установка дедлайна если не указан

DESIGN GOALS ALIGNMENT:
    - Scalability: Stateless service
    - Reliability: Transaction safety
    - Security: Input validation
    - Speed: Minimal DB queries
"""

from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from .models import Message


class MessageService:
    """
    Сервис для работы с сообщениями и перепиской.
    
    Architectural invariant:
    - Все методы статические (stateless)
    - Все операции в транзакции
    - Нет бизнес-логики в models
    """
    
    @staticmethod
    @transaction.atomic
    def send_message(
        name: str,
        email: str,
        text: str,
        parent_message=None,
        response_deadline=None
    ) -> Message:
        """
        Создать новое сообщение или ответ.
        
        Args:
            name: Имя отправителя
            email: Email отправителя
            text: Текст сообщения
            parent_message: Родительское сообщение (None для корневого)
            response_deadline: Дедлайн для ответа (None = автоустановка)
        
        Returns:
            Message: Созданное сообщение
        
        Raises:
            ValueError: Если данные невалидны
        """
        # Валидация входных данных
        if not name or not name.strip():
            raise ValueError("Имя не может быть пустым")
        
        if not email or not email.strip():
            raise ValueError("Email не может быть пустым")
        
        if not text or not text.strip():
            raise ValueError("Текст не может быть пустым")
        
        # Автоустановка дедлайна если не указан
        if not response_deadline and not parent_message:
            response_deadline = timezone.now() + timedelta(hours=24)
        
        # Создание сообщения
        message = Message.objects.create(
            name=name.strip(),
            email=email.strip(),
            text=text.strip(),
            parent_message=parent_message,
            is_read=False,
            response_deadline=response_deadline
        )
        
        return message
    
    @staticmethod
    @transaction.atomic
    def mark_as_read(message_id: int) -> Message:
        """
        Пометить сообщение как прочитанное.
        
        Args:
            message_id: ID сообщения
        
        Returns:
            Message: Обновленное сообщение
        
        Raises:
            Message.DoesNotExist: Если сообщение не найдено
        """
        message = Message.objects.get(id=message_id)
        message.is_read = True
        message.save(update_fields=['is_read', 'updated_at'])
        return message
    
    @staticmethod
    @transaction.atomic
    def mark_as_unread(message_id: int) -> Message:
        """
        Пометить сообщение как непрочитанное.
        
        Args:
            message_id: ID сообщения
        
        Returns:
            Message: Обновленное сообщение
        """
        message = Message.objects.get(id=message_id)
        message.is_read = False
        message.save(update_fields=['is_read', 'updated_at'])
        return message
    
    @staticmethod
    @transaction.atomic
    def set_response_deadline(message_id: int, hours: int = 24) -> Message:
        """
        Установить дедлайн для ответа.
        
        Args:
            message_id: ID сообщения
            hours: Количество часов до дедлайна
        
        Returns:
            Message: Обновленное сообщение
        """
        message = Message.objects.get(id=message_id)
        message.response_deadline = timezone.now() + timedelta(hours=hours)
        message.save(update_fields=['response_deadline', 'updated_at'])
        return message
    
    @staticmethod
    def get_overdue_messages():
        """
        Получить все просроченные сообщения.
        
        Returns:
            QuerySet: Список просроченных сообщений
        """
        now = timezone.now()
        return Message.objects.filter(
            response_deadline__lt=now,
            parent_message__isnull=True,
            replies__isnull=True
        ).distinct()
    
    @staticmethod
    def get_messages_with_upcoming_deadline(hours: int = 24):
        """
        Получить сообщения с приближающимся дедлайном.
        
        Args:
            hours: Количество часов до дедлайна
        
        Returns:
            QuerySet: Список сообщений
        """
        now = timezone.now()
        deadline_threshold = now + timedelta(hours=hours)
        
        return Message.objects.filter(
            response_deadline__gt=now,
            response_deadline__lte=deadline_threshold,
            parent_message__isnull=True
        ).exclude(
            replies__isnull=False
        )
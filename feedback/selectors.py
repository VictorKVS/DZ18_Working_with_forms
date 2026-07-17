"""
FILE: selectors.py
PATH: feedback/selectors.py
PURPOSE:
    Чистые запросы к БД (read-only operations) для приложения feedback.

RESPONSIBILITY:
    - Получение списка сообщений с фильтрацией
    - Получение деталей сообщения и связанных ответов
    - Получение сообщений конкретного пользователя по email

INPUT DATA:
    - include_replies: bool
    - only_unread: bool
    - message_id: int
    - user_email: str

OUTPUT DATA:
    - QuerySet[Message] или Message instance

UPSTREAM:
    - feedback/views.py
    - accounts/views.py

DOWNSTREAM:
    - feedback/models.py (Message)

DATA FLOW:
    View -> Selector -> DB -> View

ARCHITECTURAL GUARANTEES:
    - Только чтение (no side effects)
    - Оптимизированные запросы (select_related, prefetch_related)
    - Fail-fast валидация входных данных
"""

from django.db.models import QuerySet
from django.utils import timezone
from .models import Message


def get_all_messages(
    include_replies: bool = False,
    only_unread: bool = False,
    only_overdue: bool = False
) -> QuerySet:
    """Получить список сообщений с возможной фильтрацией."""
    queryset = Message.objects.all()
    
    if not include_replies:
        queryset = queryset.filter(parent_message__isnull=True)
    
    if only_unread:
        queryset = queryset.filter(is_read=False)
        
    if only_overdue:
        now = timezone.now()
        queryset = queryset.filter(
            response_deadline__lt=now,
            parent_message__isnull=True,
            replies__isnull=True
        ).distinct()
    
    return queryset.select_related('parent_message').prefetch_related('replies').order_by('-created_at')


def get_message_by_id(message_id: int) -> Message:
    """Получить сообщение по ID с предзагрузкой связей."""
    return Message.objects.select_related('parent_message').prefetch_related('replies').get(id=message_id)


def get_replies_for_message(message_id: int) -> QuerySet:
    """Получить все ответы на конкретное сообщение, отсортированные по времени."""
    return Message.objects.filter(parent_message_id=message_id).order_by('created_at')


def get_root_messages() -> QuerySet:
    """Получить только корневые сообщения (без ответов)."""
    return Message.objects.filter(parent_message__isnull=True).prefetch_related('replies').order_by('-created_at')


def get_overdue_messages() -> QuerySet:
    """Получить все просроченные сообщения."""
    now = timezone.now()
    return Message.objects.filter(
        response_deadline__lt=now,
        parent_message__isnull=True
    ).exclude(
        replies__isnull=False
    ).order_by('-created_at')


def get_messages_by_user_email(user_email: str) -> QuerySet:
    """
    Получить все сообщения конкретного пользователя по его email.
    Используется в accounts/views.py для отображения истории переписки в профиле.
    
    Args:
        user_email: Email пользователя (обязательный, не пустой)
    
    Returns:
        QuerySet: Список сообщений пользователя, отсортированный по дате создания (новые первыми)
    
    Raises:
        ValueError: Если email пустой или None
    """
    # Fail-fast валидация
    if not user_email or not user_email.strip():
        raise ValueError("user_email cannot be empty")
    
    # Нормализация email (case-insensitive)
    normalized_email = user_email.strip().lower()
    
    # Оптимизированный запрос
    return (
        Message.objects
        .filter(email__iexact=normalized_email)
        .select_related('parent_message')
        .prefetch_related('replies')
        .order_by('-created_at')
    )
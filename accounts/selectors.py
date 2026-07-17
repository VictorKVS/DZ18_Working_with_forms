"""
accounts/selectors.py
=====================

🏛️ Роль: Функции ЧТЕНИЯ данных (Query-слой в CQRS-lite).
         Отделяет логику чтения от логики записи (services.py).
         Это СЛОЙ, который будет импортировать AI-агент для получения данных.

📥 Входные данные: Критерии поиска (email, username, limit).
📤 Выходные данные: QuerySet или отдельные объекты User.

🤖 Agent-friendly API:
    from accounts.selectors import get_recent_users, get_user_stats
    
    # Агент получает последних пользователей
    users = get_recent_users(limit=10)
    
    # Агент получает статистику
    stats = get_user_stats()

💡 Почему CQRS-lite:
    - Services.py — запись (Create, Update, Delete)
    - Selectors.py — чтение (Read)
    - Это упрощает тестирование и масштабирование
"""

from django.contrib.auth import get_user_model
from django.db.models import QuerySet, Count
from typing import Dict, Any, Optional

User = get_user_model()


def get_recent_users(limit: int = 10) -> QuerySet:
    """
    Получает последних зарегистрированных пользователей.
    
    Args:
        limit: Количество пользователей (по умолчанию 10)
        
    Returns:
        QuerySet: Отсортированный по дате регистрации (новые сверху)
        
    Example:
        >>> users = get_recent_users(limit=5)
        >>> for user in users:
        ...     print(user.username, user.date_joined)
    """
    return User.objects.order_by('-date_joined')[:limit]


def get_user_stats() -> Dict[str, Any]:
    """
    Возвращает статистику по пользователям.
    
    Returns:
        Dict: {
            'total_users': int — общее количество,
            'active_users': int — активных (is_active=True),
            'staff_users': int — сотрудников (is_staff=True)
        }
        
    Example:
        >>> stats = get_user_stats()
        >>> print(f"Всего: {stats['total_users']}, активных: {stats['active_users']}")
    """
    return {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'staff_users': User.objects.filter(is_staff=True).count(),
    }


def get_user_by_username(username: str) -> Optional[User]:
    """
    Получает пользователя по username.
    
    Args:
        username: Имя пользователя
        
    Returns:
        User: Если найден
        None: Если не найден
    """
    try:
        return User.objects.get(username=username)
    except User.DoesNotExist:
        return None
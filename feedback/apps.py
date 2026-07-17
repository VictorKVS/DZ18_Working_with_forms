"""
messages/apps.py
================

🏛️ Роль: "Паспорт" приложения messages.
"""

from django.apps import AppConfig


class FeedbackConfig(AppConfig):
    """Конфигурация приложения сообщений."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'feedback'
    verbose_name = 'Система сообщений'
    
    def ready(self):
        """Зарезервировано для будущих сигналов."""
        pass

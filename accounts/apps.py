"""
accounts/apps.py
================

🏛️ Роль: "Паспорт" приложения accounts в экосистеме Django.
         Определяет человекочитаемое имя для админ-панели.

📥 Входные данные: Django автоматически импортирует при старте.
📤 Выходные данные: Регистрация приложения в реестре Django.
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """
    Конфигурация приложения аутентификации.
    
    Инварианты:
        - name строго равно 'accounts' (имя модуля)
        - verbose_name — человекочитаемое название на русском
        - default_auto_field — BigAutoField (64-bit integer)
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'Аутентификация пользователей'
    
    def ready(self):
        """
        Хук, вызываемый при старте Django.
        Зарезервирован для будущих сигналов (например, отправка email
        после регистрации).
        """
        pass
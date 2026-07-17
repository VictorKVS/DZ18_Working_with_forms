"""
accounts/urls.py
================

🏛️ Роль: Маршруты приложения аутентификации.
         Связывает URL с view-функциями.

📥 Входные данные: URL-путь (например, /accounts/register/).
📤 Выходные данные: Вызов соответствующей view-функции.

💡 app_name='accounts' — пространство имён для {% url 'accounts:register' %}
"""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
]
"""
accounts/models.py
==================

🏛️ Роль: Модели приложения аутентификации.
         В нашем проекте мы используем ВСТРОЕННУЮ модель User Django.
         Поэтому этот файл остаётся пустым (только docstring).

📥 Входные данные: Нет.
📤 Выходные данные: Нет.

💡 Почему встроенный User, а не свой:
    - ТЗ разрешает: "Используйте встроенную модель User Django ИЛИ создайте свою"
    - Встроенный User УЖЕ имеет: username, email, password (хэш), is_active, is_staff
    - Для учебной задачи этого достаточно
    - В production можно мигрировать на кастомный User через AbstractUser
"""

# Пустой файл — используем django.contrib.auth.models.User
# Если в будущем понадобится расширить модель (например, добавить phone_number),
# создадим Profile-модель с OneToOneField на User:
#
# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     phone_number = models.CharField(max_length=20)
#     bio = models.TextField()
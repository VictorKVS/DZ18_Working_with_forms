"""
accounts/tests.py
=================

🏛️ Роль: TDD-тесты — юридический контракт системы.
         Каждый тест — спецификация поведения.
         Агент читает тесты, чтобы понять, как работает сервис.

📥 Входные данные: Django Test Client (эмулятор HTTP).
📤 Выходные данные: Отчёт о прохождении тестов.

🔗 Traceability (связь с ТЗ):
    - test_01 → ТЗ п.3 "пароли совпадают"
    - test_02 → ТЗ п.3 "email уникален"
    - test_03 → ТЗ п.4 "после регистрации — редирект"
    - test_04 → ТЗ п.6 "страница профиля"
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .forms import CustomUserCreationForm
from .services import UserService

User = get_user_model()


class AccountFormsTestCase(TestCase):
    """Тесты форм аутентификации."""
    
    def setUp(self):
        """Создаёт существующего пользователя для тестов на дубликаты."""
        self.existing_user = User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='StrongPass123!'
        )
    
    def test_01_password_mismatch_validation(self):
        """
        ТЗ п.3: Форма отклоняет несовпадающие пароли.
        
        Arrange: Данные с разными password1 и password2.
        Act: Валидация формы.
        Assert: Форма невалидна, ошибка в password2 или __all__.
        """
        form = CustomUserCreationForm(data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'StrongPass123!',
            'password2': 'DifferentPass456!'
        })
        self.assertFalse(form.is_valid())
        has_error = 'password2' in form.errors or '__all__' in form.errors
        self.assertTrue(has_error)
    
    def test_02_duplicate_email_validation(self):
        """
        ТЗ п.3: Форма отклоняет уже зарегистрированный email.
        
        Arrange: Пользователь с email 'existing@example.com' существует.
        Act: Попытка регистрации с тем же email.
        Assert: Форма невалидна, ошибка в поле email.
        """
        form = CustomUserCreationForm(data={
            'username': 'newuser',
            'email': 'existing@example.com',  # Уже занят
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class AccountServicesTestCase(TestCase):
    """Тесты бизнес-логики (services.py)."""
    
    def test_03_create_user_success(self):
        """
        UserService создаёт пользователя с валидными данными.
        
        Arrange: Валидные данные.
        Act: UserService.create_user().
        Assert: Пользователь создан, email нормализован.
        """
        user = UserService.create_user(
            username='testuser',
            email='Test@Example.COM',  # Разный регистр
            password='StrongPass123!'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')  # Нормализован
        self.assertTrue(user.check_password('StrongPass123!'))
    
    def test_04_create_user_duplicate_email_raises(self):
        """
        UserService отклоняет дублирующийся email.
        
        Arrange: Пользователь с email 'dup@test.com' существует.
        Act: Попытка создать второго с тем же email.
        Assert: ValidationError.
        """
        User.objects.create_user(
            username='existing',
            email='dup@test.com',
            password='pass'
        )
        with self.assertRaises(ValidationError):
            UserService.create_user(
                username='newuser',
                email='dup@test.com',
                password='StrongPass123!'
            )


class AccountViewsTestCase(TestCase):
    """Тесты HTTP-представлений."""
    
    def test_05_register_redirect_on_success(self):
        """
        ТЗ п.4: После успешной регистрации — редирект на /home/.
        
        Arrange: Валидные данные для регистрации.
        Act: POST-запрос на /accounts/register/.
        Assert: Статус 302, пользователь создан.
        """
        url = reverse('accounts:register')
        response = self.client.post(url, {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_06_profile_requires_login(self):
        """
        ТЗ п.6: Страница профиля недоступна для анонимных.
        
        Arrange: Клиент не аутентифицирован.
        Act: GET-запрос на /accounts/profile/.
        Assert: Статус 302, редирект на /accounts/login/.
        """
        url = reverse('accounts:profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_07_profile_accessible_for_authenticated(self):
        """
        ТЗ п.6: Аутентифицированный пользователь видит профиль.
        
        Arrange: Клиент аутентифицирован.
        Act: GET-запрос на /accounts/profile/.
        Assert: Статус 200, используется шаблон profile.html.
        """
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='StrongPass123!'
        )
        self.client.login(username='testuser', password='StrongPass123!')
        url = reverse('accounts:profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')
"""
accounts/forms.py
=================

🏛️ Роль: Формы для аутентификации (Presentation Layer).
         CustomUserCreationForm расширяет встроенный UserCreationForm,
         добавляя кастомную валидацию email.

📥 Входные данные: request.POST из views.py.
📤 Выходные данные: Валидированный объект формы или form.errors.

🔒 Безопасность:
    - Пароли хэшируются автоматически (create_user())
    - Email проверяется на уникальность (clean_email())
    - Все поля экранируются от XSS (Django templates)
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


class CustomUserCreationForm(UserCreationForm):
    """
    Форма регистрации с кастомной валидацией email.
    
    Инварианты:
        - Email должен быть уникальным (проверка в clean_email())
        - Пароли должны совпадать (проверка в родительском классе)
        - Все поля обязательны
    
    Использование:
        >>> form = CustomUserCreationForm(data={...})
        >>> if form.is_valid():
        ...     user = form.save()
    """
    
    # Добавляем поле email (в UserCreationForm его нет по умолчанию)
    email = forms.EmailField(
        required=True,
        label="Электронная почта",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your@email.com'
        })
    )
    
    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2')
        labels = {
            'username': 'Имя пользователя',
            'email': 'Электронная почта',
            'password1': 'Пароль',
            'password2': 'Подтверждение пароля',
        }
    
    def __init__(self, *args, **kwargs):
        """Добавляет Bootstrap-классы ко всем полям автоматически."""
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.EmailInput, forms.PasswordInput)):
                field.widget.attrs.setdefault('class', 'form-control')
    
    def clean_email(self):
        """
        Кастомный валидатор: email должен быть уникальным.
        
        Почему именно здесь:
        - clean_<field>() вызывается автоматически при form.is_valid()
        - Это стандартный паттерн Django для валидации одного поля
        
        Raises:
            forms.ValidationError: Если email уже зарегистрирован
        """
        email = self.cleaned_data.get('email', '').strip().lower()
        User = get_user_model()
        
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "Этот email уже зарегистрирован. "
                "Используйте другой или войдите в систему."
            )
        
        return email
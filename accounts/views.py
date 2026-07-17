"""
accounts/views.py
=================

🏛️ Роль: HTTP-обёртка над UserService.
         Views — ТОЛЬКО координируют HTTP-запросы.
         Вся бизнес-логика — в services.py.
         
         Это позволяет:
         - Агенту использовать UserService напрямую (без HTTP)
         - Тестировать бизнес-логику отдельно от HTTP
         - Легко менять HTTP-слой, не трогая логику

📥 Входные данные: HttpRequest от клиента.
📤 Выходные данные: HttpResponse или HttpResponseRedirect.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm
from .services import UserService
from feedback.selectors import get_messages_by_user_email
import logging

logger = logging.getLogger(__name__)


def register(request):
    """
    Регистрация нового пользователя.
    
    Логика:
        1. GET — показать пустую форму
        2. POST — валидировать и создать пользователя
        3. После успеха — автоматический вход + редирект на /home/
    
    Почему view тонкая:
        - Вся бизнес-логика в UserService.create_user()
        - View только координирует: форма → сервис → вход → редирект
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Используем СЕРВИС (агент может сделать то же самое)
            user = UserService.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1']
            )
            
            # Автоматический вход после регистрации
            login(request, user)
            
            # Flash-сообщение для пользователя
            messages.success(request, f"Добро пожаловать, {user.username}!")
            
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    """
    Страница профиля пользователя.
    
    Требование ТЗ п.6: "Реализуйте страницу профиля пользователя,
    где отображаются его данные и отправленные сообщения."
    
    @login_required — защита от анонимных пользователей.
    Если не аутентифицирован — редирект на LOGIN_URL.
    """
    # Получаем сообщения пользователя через SELECTOR (agent-friendly)
    user_messages = get_messages_by_user_email(request.user.email)
    
    logger.info(f"Пользователь {request.user.username} открыл профиль")
    
    return render(request, 'accounts/profile.html', {
        'user_messages': user_messages,
    })

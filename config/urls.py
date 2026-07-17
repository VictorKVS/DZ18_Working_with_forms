"""
config/urls.py
==============

🏛️ Роль: Глобальный маршрутизатор проекта.
         "Диспетчерская вышка" — направляет каждый HTTP-запрос
         в нужное приложение по префиксу URL.

📥 Входные данные: Любой HTTP-запрос от клиента.
📤 Выходные данные: Вызов соответствующего view-функции.

🔒 Безопасность:
    - Admin-панель доступна только суперпользователям
    - Logout — только через POST (защита от CSRF-атак)
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

# =============================================================================
# ГЛАВНЫЕ МАРШРУТЫ
# =============================================================================
# Почему порядок важен: Django проверяет path() сверху вниз.
# Более специфичные маршруты должны идти раньше общих.
urlpatterns = [
    # Админ-панель Django
    path('admin/', admin.site.urls),
    
    # Приложение аутентификации
    # Все URL, начинающиеся с 'accounts/', делегируются в accounts/urls.py
    path('accounts/', include('accounts.urls')),
    
    # Встроенные auth-views (login/logout)
    # Почему не пишем свои: "Don't Reinvent the Wheel"
    # Django уже сделал это безопасно и протестировано
    path(
        'accounts/login/',
        auth_views.LoginView.as_view(template_name='accounts/login.html'),
        name='login'
    ),
    path(
        'accounts/logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),
    
    # Приложение сообщений
    path('feedback/', include('feedback.urls')),
    
    # Главная страница (TemplateView — generic view)
    # Почему TemplateView, а не своя функция: декларативнее, чище
    path('home/', TemplateView.as_view(template_name='home.html'), name='home'),
    path('', TemplateView.as_view(template_name='home.html'), name='index'),
]

# Раздача media-файлов ТОЛЬКО в режиме разработки
# В production это должен делать Nginx/Apache, а не Django
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

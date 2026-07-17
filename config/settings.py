"""
config/settings.py
==================

🏛️ Роль: Центральный "пульт управления" Django-проекта.
         Определяет, какие приложения активны, как логировать,
         куда перенаправлять после входа/выхода.

📥 Входные данные: Импортируется Django при каждом запуске сервера.
📤 Выходные данные: Глобальный объект settings.

🔒 Безопасность:
    - SECRET_KEY в production брать из переменных окружения
    - DEBUG = False в production
    - ALLOWED_HOSTS заполнить реальными доменами
"""

import os
from pathlib import Path

# Базовые пути
BASE_DIR = Path(__file__).resolve().parent.parent

# Безопасность (в production SECRET_KEY из .env!)
SECRET_KEY = 'django-insecure-change-me-in-production-abc123xyz'
DEBUG = True
ALLOWED_HOSTS = []

# =============================================================================
# РЕГИСТРАЦИЯ ПРИЛОЖЕНИЙ
# =============================================================================
# Почему порядок важен: Django обрабатывает приложения сверху вниз.
# Встроенные — первыми (они предоставляют базовый функционал),
# наши — после (они используют функционал встроенных).
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'feedback',
]

# Middleware — промежуточные слои обработки запросов
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',              # 🔒 Защита от CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware', # 🔒 Защита от clickjacking
]

ROOT_URLCONF = 'config.urls'

# Шаблоны
# Почему APP_DIRS = True: Django сам ищет шаблоны в <app>/templates/
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# База данных (SQLite для разработки)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Валидация паролей (стандартная, но важная!)
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Локализация
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# Статические файлы
STATIC_URL = 'static/'

# Медиа-файлы (загруженные пользователями)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# =============================================================================
# ПЕРЕНАПРАВЛЕНИЯ ПОСЛЕ АУТЕНТИФИКАЦИИ
# =============================================================================
# Почему это важно: Встроенные LoginView/LogoutView используют эти настройки.
# Без них Django не знает, куда редиректить после входа/выхода.
LOGIN_REDIRECT_URL = '/home/'      # После успешного входа
LOGOUT_REDIRECT_URL = '/'          # После выхода
LOGIN_URL = '/accounts/login/'     # Страница входа (для @login_required)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# ЛОГИРОВАНИЕ ("Чёрный ящик" для аудита)
# =============================================================================
# Почему это критично для военных/медицинских систем:
# - Каждое действие пользователя должно быть зафиксировано
# - Логи — основа для расследования инцидентов
# - Формат [время] [уровень] модуль: сообщение — стандарт индустрии
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] [{levelname}] {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'accounts': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'messages': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
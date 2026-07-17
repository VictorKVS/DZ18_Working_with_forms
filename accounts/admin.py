from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

User = get_user_model()

# Отменяем стандартную регистрацию User от django.contrib.auth
admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Кастомная конфигурация админ-панели для User."""
    list_display = ('username', 'email', 'first_name', 'last_name',
                    'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)

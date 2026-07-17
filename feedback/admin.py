"""
FILE: admin.py
PATH: feedback/admin.py
PURPOSE:
    Регистрация модели Message в Django Admin.

RESPONSIBILITY:
    - Отображение сообщений в админке
    - Фильтрация по статусу (прочитано/не прочитано)
    - Фильтрация по срокам (просрочено/в срок)
    - Поиск по имени, email, тексту

INPUT DATA:
    - Message model (from .models)

OUTPUT DATA:
    - Admin interface for Message

UPSTREAM:
    - Django admin autodiscover

DOWNSTREAM:
    - Django admin UI

DATA FLOW:
    Django Admin UI → MessageAdmin → Message (DB)

ARCHITECTURAL GUARANTEES:
    - Импортируется ТОЛЬКО существующая модель Message
    - Нет бизнес-логики в admin.py
    - Только отображение и фильтрация
"""

from django.contrib import admin
from .models import Message  # ✅ ИСПРАВЛЕНО: было UserMessage


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Админка для модели Message."""
    
    list_display = (
        'id',
        'name',
        'email',
        'short_text',
        'is_read',
        'is_overdue_display',
        'response_deadline',
        'created_at',
        'parent_message'
    )
    
    list_filter = (
        'is_read',
        'created_at',
        'response_deadline'
    )
    
    search_fields = (
        'name',
        'email',
        'text'
    )
    
    readonly_fields = (
        'created_at',
        'updated_at'
    )
    
    list_editable = ('is_read',)
    
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'email', 'text')
        }),
        ('Статус и сроки', {
            'fields': ('is_read', 'response_deadline')
        }),
        ('Переписка', {
            'fields': ('parent_message',)
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def short_text(self, obj):
        """Короткий текст для отображения в списке."""
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    short_text.short_description = 'Текст'
    
    def is_overdue_display(self, obj):
        """Отображение статуса просрочки."""
        if obj.is_overdue():
            return '⚠️ Просрочено'
        return '✅ В срок'
    is_overdue_display.short_description = 'Статус срока'
    is_overdue_display.admin_order_field = 'response_deadline'
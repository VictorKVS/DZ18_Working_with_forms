"""
FILE: models.py
PATH: feedback/models.py
PURPOSE:
    Модель сообщения с поддержкой переписки и сроков ответов.

RESPONSIBILITY:
    - Хранить сообщения пользователей
    - Поддерживать иерархию (parent_message для ответов)
    - Отслеживать статус прочтения (is_read)
    - Хранить дедлайн ответа (response_deadline)
    - Метаданные (name, email, text, created_at)

INPUT DATA:
    - name: str
    - email: str
    - text: str
    - parent_message: Message | None
    - response_deadline: datetime | None

OUTPUT DATA:
    - Message instance (saved to DB)

UPSTREAM:
    - feedback/services.py (создание сообщений)
    - feedback/views.py (HTTP запросы)

DOWNSTREAM:
    - feedback/selectors.py (чтение данных)
    - feedback/admin.py (админка)

DATA FLOW:
    View → Service → Message (DB) → Selector → View

ARCHITECTURAL GUARANTEES:
    - parent_message может быть None (корневое сообщение)
    - is_read по умолчанию False
    - created_at автоматически устанавливается
    - email валидируется Django EmailField
    - response_deadline опционально

DESIGN GOALS ALIGNMENT:
    - Scalability: Индексы на parent_message, is_read, response_deadline
    - Reliability: NOT NULL constraints где нужно
    - Security: Email validation
    - Speed: Query optimization через индексы
"""

from django.db import models
from django.utils import timezone
from datetime import timedelta


class Message(models.Model):
    """
    Модель сообщения с поддержкой переписки и сроков ответов.
    
    Architectural invariant:
    - parent_message = None → корневое сообщение
    - parent_message != None → ответ на другое сообщение
    - response_deadline = None → нет дедлайна
    - response_deadline != None → есть дедлайн для ответа
    """
    
    # === REQUIRED FIELDS ===
    name = models.CharField(
        max_length=100,
        verbose_name="Имя отправителя",
        help_text="Имя пользователя, отправившего сообщение"
    )
    
    email = models.EmailField(
        verbose_name="Email",
        help_text="Email отправителя для обратной связи"
    )
    
    text = models.TextField(
        verbose_name="Текст сообщения",
        help_text="Содержание сообщения"
    )
    
    # === OPTIONAL FIELDS ===
    parent_message = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name="Родительское сообщение",
        help_text="Сообщение, на которое дан ответ (None для корневых)"
    )
    
    is_read = models.BooleanField(
        default=False,
        verbose_name="Прочитано",
        help_text="Флаг прочтения сообщения администратором"
    )
    
    response_deadline = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дедлайн ответа",
        help_text="Срок, до которого необходимо ответить на сообщение"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
        help_text="Автоматически устанавливается при создании"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления",
        help_text="Автоматически обновляется при изменении"
    )
    
    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['parent_message']),
            models.Index(fields=['is_read']),
            models.Index(fields=['response_deadline']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.email}) - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    def is_reply(self):
        """Проверить, является ли сообщение ответом."""
        return self.parent_message is not None
    
    def get_replies_count(self):
        """Получить количество ответов на это сообщение."""
        return self.replies.count()
    
    def is_overdue(self):
        """Проверить, просрочен ли дедлайн ответа."""
        if not self.response_deadline:
            return False
        return timezone.now() > self.response_deadline and not self.replies.exists()
    
    def get_time_remaining(self):
        """Получить оставшееся время до дедлайна."""
        if not self.response_deadline:
            return None
        
        now = timezone.now()
        if now > self.response_deadline:
            return "Просрочено"
        
        delta = self.response_deadline - now
        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        
        if days > 0:
            return f"{days} дн. {hours} ч."
        elif hours > 0:
            return f"{hours} ч. {minutes} мин."
        else:
            return f"{minutes} мин."
    
    def set_default_deadline(self, hours=24):
        """Установить дедлайн по умолчанию (24 часа)."""
        self.response_deadline = timezone.now() + timedelta(hours=hours)
        self.save(update_fields=['response_deadline'])
"""
accounts/services.py
====================

🏛️ Роль: БИЗНЕС-ЛОГИКА аутентификации, отделённая от HTTP-слоя.
         Это СЛОЙ, который будет импортировать AI-агент.
         Views — только тонкая обёртка над этим сервисом.

📥 Входные данные: Валидированные данные из форм или напрямую от агента.
📤 Выходные данные: Объекты User или исключения.

🤖 Agent-friendly API:
    from accounts.services import UserService
    
    # Агент создаёт пользователя
    user = UserService.create_user('ivan', 'ivan@test.com', 'StrongPass123!')
    
    # Агент аутентифицирует пользователя
    user = UserService.authenticate('ivan', 'StrongPass123!')

🔒 Безопасность:
    - Пароли хэшируются автоматически (create_user)
    - Email нормализуется (lowercase)
    - Все действия логируются для аудита
"""

from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError
from typing import Optional
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class UserService:
    """
    Сервис для работы с пользователями.
    
    Все методы статические — сервис не хранит состояние.
    Это позволяет легко тестировать и использовать из агентов.
    """
    
    @staticmethod
    def create_user(username: str, email: str, password: str) -> User:
        """
        Создаёт нового пользователя с нормализованным email.
        
        Args:
            username: Уникальное имя (макс. 150 символов)
            email: Уникальный email (RFC 5321, будет нормализован)
            password: Пароль (будет хэширован через create_user)
        
        Returns:
            User: Созданный пользователь
            
        Raises:
            ValidationError: Если username или email уже заняты
            
        Side Effects:
            - Запись в БД (создание пользователя)
            - Запись в лог аудита
        """
        # Нормализация email
        email = email.strip().lower()
        
        # Проверка уникальности (двойная защита: форма + сервис)
        if User.objects.filter(email=email).exists():
            logger.warning(f"AUDIT | CREATE_USER_FAILED | reason=duplicate_email | email={email}")
            raise ValidationError(f"Email '{email}' уже зарегистрирован")
        
        if User.objects.filter(username=username).exists():
            logger.warning(f"AUDIT | CREATE_USER_FAILED | reason=duplicate_username | username={username}")
            raise ValidationError(f"Username '{username}' уже занят")
        
        # Создание пользователя (create_user автоматически хэширует пароль!)
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        # Аудит-лог (для военных/медицинских систем — обязательно!)
        logger.info(
            f"AUDIT | CREATE_USER | user={username} | email={email} | id={user.id}"
        )
        
        return user
    
    @staticmethod
    def authenticate(username: str, password: str) -> Optional[User]:
        """
        Аутентифицирует пользователя по username и паролю.
        
        Args:
            username: Имя пользователя
            password: Пароль (в открытом виде, сравнивается с хэшем)
            
        Returns:
            User: Если аутентификация успешна
            None: Если учётные данные неверны
            
        Side Effects:
            - Запись в лог аудита (успех/неудача)
        """
        user = authenticate(username=username, password=password)
        
        if user:
            logger.info(f"AUDIT | LOGIN_SUCCESS | user={username}")
        else:
            logger.warning(f"AUDIT | LOGIN_FAILED | user={username}")
        
        return user
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """
        Получает пользователя по email.
        
        Args:
            email: Email пользователя (будет нормализован)
            
        Returns:
            User: Если найден
            None: Если не найден
        """
        try:
            return User.objects.get(email=email.strip().lower())
        except User.DoesNotExist:
            return None
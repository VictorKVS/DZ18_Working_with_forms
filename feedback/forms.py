"""
FILE: forms.py
PATH: feedback/forms.py
PURPOSE:
    Формы для валидации входных данных.

RESPONSIBILITY:
    - Валидация формы отправки сообщения
    - Валидация формы ответа
    - Очистка данных (cleaning)

INPUT DATA:
    - request.POST data

OUTPUT DATA:
    - cleaned_data: dict

UPSTREAM:
    - feedback/views.py (HTTP handlers)

DOWNSTREAM:
    - feedback/services.py (business logic)

DATA FLOW:
    User → Form → View → Service → DB

ARCHITECTURAL GUARANTEES:
    - Все поля валидируются
    - Ошибки возвращаются пользователю
    - Нет бизнес-логики в формах
"""

from django import forms


class UserMessageForm(forms.Form):
    """
    Форма для отправки сообщения пользователем.
    
    Fields:
        - name: CharField (required, max_length=100)
        - email: EmailField (required)
        - text: CharField (required, widget=Textarea)
    """
    
    name = forms.CharField(
        max_length=100,
        label="Ваше имя",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваше имя'
        })
    )
    
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@mail.com'
        })
    )
    
    text = forms.CharField(
        label="Сообщение",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваше сообщение',
            'rows': 5
        })
    )


class ReplyMessageForm(forms.Form):
    """
    Форма для ответа на сообщение.
    
    Fields:
        - reply_text: CharField (required, widget=Textarea)
    """
    
    reply_text = forms.CharField(
        label="Ваш ответ",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваш ответ',
            'rows': 4
        })
    )
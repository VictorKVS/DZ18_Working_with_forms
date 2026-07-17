"""
FILE: views.py
PATH: feedback/views.py
PURPOSE:
    HTTP-обёртки над MessageService и селекторами.
    Поддерживает ДВА режима: Обычный HTTP и Ajax (JSON).

RESPONSIBILITY:
    - Приём HTTP-запросов (GET/POST)
    - Валидация входных данных через формы
    - Делегирование бизнес-логики в MessageService
    - Формирование HttpResponse или JsonResponse

DATA FLOW:
    Client -> View -> Form (validate) -> Service/Selector -> DB
    DB -> Selector -> View -> JsonResponse/HttpResponse -> Client

ARCHITECTURAL GUARANTEES:
    - Thin View: Никакой бизнес-логики внутри view.
    - Fail-fast: Ошибки валидации немедленно возвращаются с кодом 400 (AJAX) 
      или рендерятся в шаблон (HTTP).
    - Security: CSRF-токен проверяется автоматически Django для POST.
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse, Http404
from django.contrib import messages as django_messages
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator

from .forms import UserMessageForm, ReplyMessageForm
from .services import MessageService
from .selectors import get_all_messages, get_message_by_id, get_replies_for_message
from .models import Message

import logging

logger = logging.getLogger(__name__)


@require_http_methods(["GET", "POST"])
def send_message(request):
    """Отправка нового сообщения (HTTP + AJAX)."""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        form = UserMessageForm(request.POST)
        if form.is_valid():
            try:
                # Делегирование бизнес-логики в сервис
                message = MessageService.send_message(
                    name=form.cleaned_data['name'],
                    email=form.cleaned_data['email'],
                    text=form.cleaned_data['text']
                )
                
                if is_ajax:
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Сообщение успешно отправлено!',
                        'message_id': message.id
                    })
                
                django_messages.success(request, "Сообщение успешно отправлено!")
                return redirect('feedback:send_message')
                
            except Exception as e:
                logger.error(f"Ошибка при отправке сообщения: {e}", exc_info=True)
                if is_ajax:
                    return JsonResponse({'status': 'error', 'message': 'Внутренняя ошибка сервера'}, status=500)
                django_messages.error(request, "Произошла ошибка при отправке.")
        else:
            # Fail-fast для AJAX при ошибках валидации
            if is_ajax:
                return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    else:
        form = UserMessageForm()
    
    return render(request, 'feedback/send_message.html', {'form': form})


@require_http_methods(["GET"])
def message_list(request):
    """Список сообщений с пагинацией (HTTP + AJAX)."""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    messages_qs = get_all_messages(include_replies=False)
    paginator = Paginator(messages_qs, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    if is_ajax:
        messages_data = [
            {
                'id': msg.id,
                'name': msg.name,
                'text_preview': msg.text[:100] + '...' if len(msg.text) > 100 else msg.text,
                'created_at': msg.created_at.strftime('%d.%m.%Y %H:%M'),
                'deadline': msg.response_deadline.strftime('%d.%m.%Y %H:%M') if msg.response_deadline else None,
                'is_overdue': msg.is_overdue(),
                'time_remaining': msg.get_time_remaining(),
                'is_read': msg.is_read,
                'replies_count': msg.get_replies_count()
            }
            for msg in page_obj
        ]
        return JsonResponse({
            'status': 'success',
            'messages': messages_data,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'has_next': page_obj.has_next(),
                'next_page': page_obj.next_page_number() if page_obj.has_next() else None
            }
        })
    
    return render(request, 'feedback/message_list.html', {'page_obj': page_obj})


@require_http_methods(["GET"])
def message_detail(request, message_id):
    """Детали сообщения и история переписки (HTTP + AJAX)."""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    # Fail-fast: безопасное получение через селектор
    try:
        message = get_message_by_id(message_id)
    except Message.DoesNotExist:
        raise Http404("Сообщение не найдено")
    
    # Бизнес-логика: помечаем как прочитанное при просмотре
    if not message.is_read:
        MessageService.mark_as_read(message_id)
    
    replies = get_replies_for_message(message_id)
    
    if is_ajax:
        replies_data = [
            {
                'id': reply.id,
                'name': reply.name,
                'text': reply.text,
                'created_at': reply.created_at.strftime('%d.%m.%Y %H:%M'),
                'is_admin': reply.parent_message is not None
            }
            for reply in replies
        ]
        return JsonResponse({
            'status': 'success',
            'message': {
                'id': message.id,
                'name': message.name,
                'email': message.email,
                'text': message.text,
                'created_at': message.created_at.strftime('%d.%m.%Y %H:%M'),
                'deadline': message.response_deadline.strftime('%d.%m.%Y %H:%M') if message.response_deadline else None,
                'is_overdue': message.is_overdue(),
                'time_remaining': message.get_time_remaining()
            },
            'replies': replies_data
        })
    
    return render(request, 'feedback/message_detail.html', {
        'message': message,
        'replies': replies,
        'reply_form': ReplyMessageForm()
    })


@require_http_methods(["POST"])
def reply_to_message(request, message_id):
    """Ответ на сообщение (HTTP + AJAX)."""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    # Fail-fast проверка существования родительского сообщения
    try:
        parent_message = get_message_by_id(message_id)
    except Message.DoesNotExist:
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': 'Сообщение не найдено'}, status=404)
        raise Http404("Сообщение не найдено")
    
    form = ReplyMessageForm(request.POST)
    if form.is_valid():
        try:
            reply = MessageService.send_message(
                name="Администратор",
                email="admin@example.com",
                text=form.cleaned_data['reply_text'],
                parent_message=parent_message
            )
            
            if is_ajax:
                return JsonResponse({
                    'status': 'success',
                    'message': 'Ответ успешно отправлен!',
                    'reply': {
                        'id': reply.id,
                        'name': reply.name,
                        'text': reply.text,
                        'created_at': reply.created_at.strftime('%d.%m.%Y %H:%M')
                    }
                })
            
            django_messages.success(request, "Ответ успешно отправлен!")
            return redirect('feedback:message_detail', message_id=message_id)
            
        except Exception as e:
            logger.error(f"Ошибка при отправке ответа: {e}", exc_info=True)
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': 'Внутренняя ошибка'}, status=500)
            django_messages.error(request, "Произошла ошибка при отправке ответа.")
    else:
        # Fail-fast для AJAX при ошибках валидации формы
        if is_ajax:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        
        # HTTP-фоллбек: возвращаем страницу с формой, содержащей ошибки валидации
        return render(request, 'feedback/message_detail.html', {
            'message': parent_message,
            'replies': get_replies_for_message(message_id),
            'reply_form': form
        })
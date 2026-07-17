"""
FILE: urls.py
PATH: feedback/urls.py
PURPOSE: Маршрутизация URL для приложения feedback.
"""
from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    path('', views.send_message, name='send_message'),
    path('list/', views.message_list, name='message_list'),
    path('<int:message_id>/', views.message_detail, name='message_detail'),
    path('<int:message_id>/reply/', views.reply_to_message, name='reply_to_message'),
]
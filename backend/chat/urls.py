"""
URL configuration for chat app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'conversations', views.ConversationViewSet, basename='conversation')

urlpatterns = [
    path('chat/', views.chat_with_agent, name='chat'),
    path('chat/history/', views.chat_history, name='chat-history'),
    path('', include(router.urls)),
]

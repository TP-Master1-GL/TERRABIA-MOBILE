# chat/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('conversations/', views.ConversationListCreateAPIView.as_view(), name='conversation-list'),
    path('conversations/<int:pk>/', views.ConversationDetailAPIView.as_view(), name='conversation-detail'),
    path('conversations/<int:pk>/messages/', views.MessageListCreateAPIView.as_view(), name='message-list'),
    
    # Nouvelles routes pour la gestion de la lecture
    path('messages/<int:message_id>/mark_read/', views.mark_message_as_read, name='mark-message-read'),
    path('conversations/<int:conversation_id>/mark_read/', views.mark_conversation_as_read, name='mark-conversation-read'),
    path('conversations/<int:conversation_id>/unread_count/', views.conversation_unread_count, name='conversation-unread-count'),
]
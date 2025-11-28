# chat/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('conversations/', views.ConversationListCreateAPIView.as_view(), name='conversation-list'),
    path('conversations/<int:pk>/', views.ConversationDetailAPIView.as_view(), name='conversation-detail'),
    path('conversations/<int:pk>/messages/', views.MessageListCreateAPIView.as_view(), name='message-list'),
]
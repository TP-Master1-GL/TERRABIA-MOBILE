# chat/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

User = get_user_model()

class ConversationListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)

    @swagger_auto_schema(
        operation_description="Liste toutes mes conversations ou en crée une nouvelle",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'participant_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID de l'autre utilisateur")
            },
            required=['participant_id']
        ),
        responses={
            200: ConversationSerializer(many=True),
            201: ConversationSerializer()
        }
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        participant_id = self.request.data.get('participant_id')
        participant = get_object_or_404(User, id=participant_id)
        conv_qs = Conversation.objects.filter(participants=self.request.user).filter(participants=participant)
        if conv_qs.exists():
            self.kwargs['pk'] = conv_qs.first().id
            return self.retrieve(request)
        conversation = serializer.save()
        conversation.participants.add(self.request.user, participant)


class ConversationDetailAPIView(generics.RetrieveAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_description="Détails d'une conversation")
    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)


class MessageListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        conv = get_object_or_404(Conversation, id=self.kwargs['pk'], participants=self.request.user)
        return conv.messages.all()

    @swagger_auto_schema(
        operation_description="Envoyer un message dans une conversation existante",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'content': openapi.Schema(type=openapi.TYPE_STRING, description="Contenu du message")
            },
            required=['content']
        ),
        responses={201: MessageSerializer()}
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        conversation = get_object_or_404(Conversation, id=self.kwargs['pk'], participants=self.request.user)
        serializer.save(sender=self.request.user, conversation=conversation)
# chat/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.utils import timezone
from users.models import User  # Importer depuis votre app users
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class ConversationListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

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


class ConversationDetailAPIView(generics.RetrieveAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @swagger_auto_schema(operation_description="Détails d'une conversation")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class MessageListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        conv = get_object_or_404(Conversation, id=self.kwargs['pk'], participants=self.request.user)
        return conv.messages.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

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


# Nouvelles vues pour la gestion de la lecture des messages
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_message_as_read(request, message_id):
    """Marquer un message comme lu"""
    try:
        message = Message.objects.get(id=message_id)
        # Vérifier que l'utilisateur fait partie de la conversation et n'est pas l'expéditeur
        if (request.user in message.conversation.participants.all() and 
            message.sender != request.user):
            message.mark_as_read()
            return Response({
                'status': 'message read', 
                'read_at': message.read_at,
                'message_id': message.id
            })
        return Response({'error': 'Non autorisé'}, status=403)
    except Message.DoesNotExist:
        return Response({'error': 'Message non trouvé'}, status=404)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_conversation_as_read(request, conversation_id):
    """Marquer tous les messages d'une conversation comme lus"""
    try:
        conversation = Conversation.objects.get(id=conversation_id, participants=request.user)
        # Marquer tous les messages non lus de l'autre participant
        unread_messages = conversation.messages.filter(
            is_read=False
        ).exclude(
            sender=request.user
        )
        
        for message in unread_messages:
            message.mark_as_read()
            
        return Response({
            'status': 'conversation read',
            'marked_count': unread_messages.count(),
            'conversation_id': conversation_id
        })
    except Conversation.DoesNotExist:
        return Response({'error': 'Conversation non trouvée'}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversation_unread_count(request, conversation_id):
    """Compter les messages non lus dans une conversation"""
    try:
        conversation = Conversation.objects.get(id=conversation_id, participants=request.user)
        unread_count = conversation.messages.filter(
            is_read=False
        ).exclude(
            sender=request.user
        ).count()
        
        return Response({
            'conversation_id': conversation_id,
            'unread_count': unread_count
        })
    except Conversation.DoesNotExist:
        return Response({'error': 'Conversation non trouvée'}, status=404)
# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message, Conversation
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'

        # Vérifier que l'utilisateur fait partie de la conversation
        if not await self.user_in_conversation():
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        user = self.scope['user']

        # Sauvegarder le message
        msg = await self.save_message(user, message)

        # Envoyer à tout le groupe
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': user.username,
                'timestamp': msg.timestamp.isoformat(),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp'],
        }))

    @database_sync_to_async
    def user_in_conversation(self):
        return Conversation.objects.filter(
            id=self.conversation_id,
            participants=self.scope['user']
        ).exists()

    @database_sync_to_async
    def save_message(self, user, content):
        conversation = Conversation.objects.get(id=self.conversation_id)
        return Message.objects.create(
            conversation=conversation,
            sender=user,
            content=content
        )
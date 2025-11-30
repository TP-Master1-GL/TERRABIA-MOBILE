# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message, Conversation
from users.models import User  # Importer depuis votre app users

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
        message_type = data.get('type', 'message')
        
        if message_type == 'message':
            await self.handle_new_message(data)
        elif message_type == 'message_read':
            await self.handle_message_read(data)

    async def handle_new_message(self, data):
        message_content = data['message']
        user = self.scope['user']

        # Sauvegarder le message
        msg = await self.save_message(user, message_content)

        # Envoyer à tout le groupe
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_content,
                'sender_id': user.id,
                'sender_username': user.username,
                'message_id': msg.id,
                'timestamp': msg.timestamp.isoformat(),
                'is_read': False
            }
        )

    async def handle_message_read(self, data):
        message_id = data['message_id']
        user = self.scope['user']
        
        # Marquer le message comme lu
        success = await self.mark_message_as_read(message_id, user)
        
        if success:
            # Notifier les autres participants
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message_read_notification',
                    'message_id': message_id,
                    'read_by_id': user.id,
                    'read_by_username': user.username,
                    'read_at': timezone.now().isoformat()
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'message_id': event['message_id'],
            'timestamp': event['timestamp'],
            'is_read': event['is_read']
        }))

    async def message_read_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message_read',
            'message_id': event['message_id'],
            'read_by_id': event['read_by_id'],
            'read_by_username': event['read_by_username'],
            'read_at': event['read_at']
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

    @database_sync_to_async
    def mark_message_as_read(self, message_id, user):
        try:
            message = Message.objects.get(id=message_id)
            # Vérifier que l'utilisateur n'est pas l'expéditeur
            if message.sender != user:
                message.mark_as_read()
                return True
        except Message.DoesNotExist:
            pass
        return False
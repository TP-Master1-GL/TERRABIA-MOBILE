# chat/serializers.py
from rest_framework import serializers
from .models import Conversation, Message
from users.models import User  # Importer depuis votre app users
from users.serializers import UserSerializer  # Utiliser votre serializer existant

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'timestamp', 'is_read', 'read_at', 'is_mine']
        read_only_fields = ['sender', 'timestamp', 'is_read', 'read_at']

    def get_is_mine(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.sender.id == request.user.id
        return False


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    other_user = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    # Champ pour la création
    participant_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Conversation
        fields = [
            'id', 'participants', 'created_at', 'updated_at', 
            'last_message', 'other_user', 'unread_count', 'participant_id'
        ]

    def get_last_message(self, obj):
        msg = obj.messages.last()
        if msg:
            return MessageSerializer(msg, context=self.context).data
        return None

    def get_other_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            other_user = obj.other_participant(request.user)
            if other_user:
                return UserSerializer(other_user).data
        return None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0

    def create(self, validated_data):
        participant_id = validated_data.pop('participant_id', None)
        request = self.context.get('request')
        
        if not participant_id or not request:
            raise serializers.ValidationError("participant_id est requis")
        
        try:
            participant = User.objects.get(id=participant_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("Utilisateur participant non trouvé")

        # Vérifier si une conversation existe déjà
        existing_conv = Conversation.objects.filter(
            participants=request.user
        ).filter(
            participants=participant
        ).first()
        
        if existing_conv:
            return existing_conv
        
        # Créer une nouvelle conversation
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, participant)
        return conversation
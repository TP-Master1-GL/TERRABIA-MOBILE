# chat/models.py
from django.db import models
from users.models import User  # Importer depuis votre app users

class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        participant_names = [f"{p.first_name} {p.last_name}" if p.first_name and p.last_name else p.username 
                           for p in self.participants.all()]
        return f"Chat entre {', '.join(participant_names)}"

    def other_participant(self, current_user):
        """Retourne l'autre participant de la conversation"""
        return self.participants.exclude(id=current_user.id).first()


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)  # Ajouter pour suivre quand le message est lu

    class Meta:
        ordering = ['timestamp']

    def mark_as_read(self):
        """Marquer le message comme lu"""
        if not self.is_read:
            self.is_read = True
            from django.utils import timezone
            self.read_at = timezone.now()
            self.save()

    def __str__(self):
        return f"{self.sender.username} → {self.content[:30]}"
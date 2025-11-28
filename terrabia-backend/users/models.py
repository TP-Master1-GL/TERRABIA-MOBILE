# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    ROLE_CHOICES = [
        ('farmer', 'Agriculteur'),
        ('buyer', 'Acheteur'),
        ('delivery', 'Livreur'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='buyer')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    # avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
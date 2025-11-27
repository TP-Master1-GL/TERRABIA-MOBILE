from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('buyer', 'Acheteur'),
        ('farmer', 'Agriculteur'),
        ('delivery_agent', 'Livreur'),   
        ('delivery_agency', 'Agence de livraison'),  
        ('admin', 'Administrateur'),
    )

    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='buyer')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Une agence peut avoir plusieurs livreurs
    delivery_agency = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='delivery_agents',
        limit_choices_to={'user_type': 'delivery_agency'}
    )

    def __str__(self):
        return self.username
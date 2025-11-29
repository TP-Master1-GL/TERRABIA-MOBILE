from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('farmer', 'Agriculteur'),
        ('buyer', 'Acheteur'),
        ('delivery', 'Agence de Livraison'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'

class FarmerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farmer_profile')
    farm_name = models.CharField(max_length=255, blank=True)  # Rendre optionnel
    farm_location = models.CharField(max_length=255, blank=True)  # Rendre optionnel
    farm_size = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # AJOUT DEFAULT
    certification = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

class BuyerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='buyer_profile')
    company_name = models.CharField(max_length=255, blank=True)
    business_type = models.CharField(max_length=255, blank=True)
    preferences = models.JSONField(default=dict, blank=True)

class DeliveryProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='delivery_profile')
    company_name = models.CharField(max_length=255, blank=True)  # Rendre optionnel
    license_number = models.CharField(max_length=255, blank=True)  # Rendre optionnel
    vehicle_type = models.CharField(max_length=100, blank=True)  # Rendre optionnel
    delivery_zones = models.JSONField(default=list)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
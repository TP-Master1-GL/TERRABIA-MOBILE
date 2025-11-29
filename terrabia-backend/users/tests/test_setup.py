from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken  # AJOUT IMPORT

User = get_user_model()

class TestSetup(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Création des utilisateurs de test
        self.farmer_data = {
            'username': 'farmer_test',
            'email': 'farmer@test.com',
            'password': 'password123',
            'password_confirm': 'password123',
            'user_type': 'farmer',
            'phone_number': '+1234567890',
            'first_name': 'Jean',
            'last_name': 'Dupont'
        }
        
        self.buyer_data = {
            'username': 'buyer_test',
            'email': 'buyer@test.com',
            'password': 'password123',
            'password_confirm': 'password123',
            'user_type': 'buyer',
            'phone_number': '+1234567891',
            'first_name': 'Marie',
            'last_name': 'Martin'
        }
        
        self.delivery_data = {
            'username': 'delivery_test',
            'email': 'delivery@test.com',
            'password': 'password123',
            'password_confirm': 'password123',
            'user_type': 'delivery',
            'phone_number': '+1234567892',
            'first_name': 'Pierre',
            'last_name': 'Durand'
        }
        
        # Créer et authentifier un utilisateur pour les tests nécessitant une auth
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            user_type='buyer'
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def tearDown(self):
        # Nettoyer proprement
        try:
            User.objects.all().delete()
        except:
            pass  # Ignorer les erreurs de transaction
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient  # AJOUT IMPORT
from rest_framework_simplejwt.tokens import RefreshToken  # AJOUT IMPORT
from .test_setup import TestSetup
from users.models import User, FarmerProfile, BuyerProfile, DeliveryProfile

class AuthenticationTests(TestSetup):
    
    def test_user_registration_farmer(self):
        """Test l'inscription d'un agriculteur"""
        url = reverse('register')
        response = self.client.post(url, self.farmer_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['user_type'], 'farmer')
        self.assertEqual(response.data['user']['username'], 'farmer_test')
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
        # Vérifier que le profil farmer a été créé
        user = User.objects.get(username='farmer_test')
        self.assertTrue(hasattr(user, 'farmer_profile'))
    
    def test_user_registration_buyer(self):
        """Test l'inscription d'un acheteur"""
        url = reverse('register')
        response = self.client.post(url, self.buyer_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['user_type'], 'buyer')
        self.assertTrue(hasattr(User.objects.get(username='buyer_test'), 'buyer_profile'))
    
    def test_user_registration_delivery(self):
        """Test l'inscription d'une agence de livraison"""
        url = reverse('register')
        response = self.client.post(url, self.delivery_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['user_type'], 'delivery')
        self.assertTrue(hasattr(User.objects.get(username='delivery_test'), 'delivery_profile'))
    
    def test_user_registration_password_mismatch(self):
        """Test l'inscription avec mots de passe différents"""
        data = self.farmer_data.copy()
        data['password_confirm'] = 'differentpassword'
        
        url = reverse('register')
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Corriger l'assertion - le message d'erreur est dans 'non_field_errors'
        self.assertIn('non_field_errors', response.data)
        self.assertIn('Les mots de passe ne correspondent pas', str(response.data['non_field_errors']))
    
    def test_user_login_success(self):
        """Test la connexion utilisateur réussie"""
        # Créer un utilisateur d'abord
        User.objects.create_user(
            username='login_test',
            password='password123',
            user_type='buyer'
        )
        
        url = reverse('login')
        data = {
            'username': 'login_test',
            'password': 'password123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['username'], 'login_test')
    
    def test_user_login_invalid_credentials(self):
        """Test la connexion avec identifiants invalides"""
        url = reverse('login')
        data = {
            'username': 'nonexistent',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
    
    def test_token_refresh(self):
        """Test le rafraîchissement du token"""
        user = User.objects.create_user(
            username='refresh_test',
            password='password123',
            user_type='buyer'
        )
        refresh = RefreshToken.for_user(user)  # IMPORT AJOUTÉ
        
        url = reverse('token_refresh')
        data = {'refresh': str(refresh)}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
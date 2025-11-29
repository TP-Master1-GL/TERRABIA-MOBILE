from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient  # AJOUT IMPORT
from rest_framework_simplejwt.tokens import RefreshToken  # AJOUT IMPORT
from .test_setup import TestSetup
from users.models import User, FarmerProfile, BuyerProfile, DeliveryProfile

class UserManagementTests(TestSetup):
    
    def test_get_user_list_authenticated(self):
        """Test la récupération de la liste des utilisateurs (authentifié)"""
        url = reverse('user-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_get_user_list_unauthenticated(self):
        """Test la récupération de la liste des utilisateurs (non authentifié)"""
        client = APIClient()  # IMPORT AJOUTÉ
        url = reverse('user-list')
        response = client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_user_detail(self):
        """Test la récupération des détails d'un utilisateur"""
        user = User.objects.create_user(
            username='detail_test',
            email='detail@test.com',
            password='password123',
            user_type='farmer'
        )
        
        url = reverse('user-detail', kwargs={'pk': user.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'detail_test')
        self.assertEqual(response.data['user_type'], 'farmer')
    
    def test_get_current_user(self):
        """Test la récupération de l'utilisateur courant"""
        url = reverse('user-me')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_update_user_profile(self):
        """Test la mise à jour du profil utilisateur"""
        url = reverse('user-me')
        data = {
            'first_name': 'Nouveau',
            'last_name': 'Nom',
            'phone_number': '+33612345678'
        }
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Nouveau')
        self.assertEqual(response.data['last_name'], 'Nom')
        self.assertEqual(response.data['phone_number'], '+33612345678')
    
    def test_delete_user(self):
        """Test la suppression d'un utilisateur"""
        user = User.objects.create_user(
            username='delete_test',
            email='delete@test.com',
            password='password123',
            user_type='buyer'
        )
        
        url = reverse('user-detail', kwargs={'pk': user.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(username='delete_test').exists())
    
    def test_farmer_profile_retrieve(self):
        """Test la récupération du profil agriculteur"""
        # Créer un farmer
        farmer = User.objects.create_user(
            username='farmer_profile_test',
            password='password123',
            user_type='farmer'
        )
        FarmerProfile.objects.create(
            user=farmer,
            farm_name='Ferme Test',
            farm_location='Paris',
            farm_size=10.5
        )
        
        # S'authentifier en tant que ce farmer
        refresh = RefreshToken.for_user(farmer)  # IMPORT AJOUTÉ
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('farmer-profile')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['farm_name'], 'Ferme Test')
        self.assertEqual(response.data['farm_location'], 'Paris')
    
    def test_buyer_profile_update(self):
        """Test la mise à jour du profil acheteur"""
        buyer = User.objects.create_user(
            username='buyer_update_test',
            password='password123',
            user_type='buyer'
        )
        BuyerProfile.objects.create(user=buyer)
        
        refresh = RefreshToken.for_user(buyer)  # IMPORT AJOUTÉ
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('buyer-profile')
        data = {
            'company_name': 'Entreprise Test',
            'business_type': 'Grossiste'
        }
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['company_name'], 'Entreprise Test')
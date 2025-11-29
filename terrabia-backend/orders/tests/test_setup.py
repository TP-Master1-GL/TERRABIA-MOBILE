from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from products.models import Product, Category
from orders.models import Cart, CartItem

User = get_user_model()

class OrderTestSetup(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # Créer des utilisateurs
        self.farmer = User.objects.create_user(
            username='test_farmer',
            email='farmer@test.com',
            password='password123',
            user_type='farmer'
        )
        
        self.buyer = User.objects.create_user(
            username='test_buyer',
            email='buyer@test.com',
            password='password123',
            user_type='buyer'
        )
        
        self.delivery = User.objects.create_user(
            username='test_delivery',
            email='delivery@test.com',
            password='password123',
            user_type='delivery'
        )
        
        # Créer une catégorie
        self.category = Category.objects.create(
            name='Légumes'
            # Pas de description dans votre modèle
        )
        
        # Créer des produits selon votre modèle
        self.product1 = Product.objects.create(
            name='Tomates',
            description='Tomates bio',
            price=2.50,
            unit='kg',
            stock=100,
            farmer=self.farmer,
            category=self.category
        )
        
        self.product2 = Product.objects.create(
            name='Carottes',
            description='Carottes fraîches',
            price=1.80,
            unit='kg',
            stock=50,
            farmer=self.farmer,
            category=self.category
        )
        
        # Authentifier le buyer par défaut
        refresh = RefreshToken.for_user(self.buyer)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Créer un panier pour le buyer
        self.cart, created = Cart.objects.get_or_create(user=self.buyer)
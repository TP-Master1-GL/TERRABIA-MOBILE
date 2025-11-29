from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .test_setup import OrderTestSetup
from orders.models import Order, OrderItem, Cart, CartItem

class OrderTests(OrderTestSetup):
    
    def setUp(self):
        super().setUp()
        # Remplir le panier pour les tests de commande
        CartItem.objects.create(
            cart=self.cart,
            product=self.product1,
            quantity=2
        )
        CartItem.objects.create(
            cart=self.cart,
            product=self.product2,
            quantity=1
        )
    
    def test_create_order_from_cart(self):
        """Test la création d'une commande à partir du panier"""
        url = reverse('order-list')
        data = {
            'shipping_address': '123 Rue Test, Paris, France',
            'delivery_fee': 5.00
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['buyer'], self.buyer.id)
        self.assertEqual(response.data['farmer'], self.farmer.id)
        self.assertEqual(response.data['status'], 'pending')
        self.assertEqual(response.data['shipping_address'], '123 Rue Test, Paris, France')
        
        # Vérifier que le panier a été vidé
        cart = Cart.objects.get(user=self.buyer)
        self.assertEqual(cart.items.count(), 0)
        
        # Vérifier les OrderItems
        order = Order.objects.get(id=response.data['id'])
        self.assertEqual(order.items.count(), 2)
        
        # Vérifier le calcul du total
        expected_total = (2 * 2.50) + (1 * 1.80) + 5.00
        self.assertEqual(float(order.total_amount), expected_total)
    
    def test_create_order_empty_cart(self):
        """Test la création d'une commande avec un panier vide"""
        # Vider le panier
        self.cart.items.all().delete()
        
        url = reverse('order-list')
        data = {
            'shipping_address': '123 Rue Test, Paris, France'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_get_orders_list_buyer(self):
        """Test la récupération de la liste des commandes pour un acheteur"""
        # Créer une commande
        order = Order.objects.create(
            buyer=self.buyer,
            farmer=self.farmer,
            shipping_address='Test Address',
            total_amount=10.00
        )
        OrderItem.objects.create(
            order=order,
            product=self.product1,
            quantity=2,
            unit_price=2.50
        )
        
        url = reverse('order-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], order.id)
        self.assertEqual(len(response.data[0]['items']), 1)
    
    def test_get_orders_list_farmer(self):
        """Test la récupération de la liste des commandes pour un agriculteur"""
        # Créer une commande
        order = Order.objects.create(
            buyer=self.buyer,
            farmer=self.farmer,
            shipping_address='Test Address',
            total_amount=10.00
        )
        
        # S'authentifier en tant que farmer
        refresh = RefreshToken.for_user(self.farmer)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('order-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['farmer'], self.farmer.id)
    
    def test_get_order_detail(self):
        """Test la récupération des détails d'une commande"""
        order = Order.objects.create(
            buyer=self.buyer,
            farmer=self.farmer,
            shipping_address='Test Address',
            total_amount=10.00
        )
        OrderItem.objects.create(
            order=order,
            product=self.product1,
            quantity=2,
            unit_price=2.50
        )
        
        url = reverse('order-detail', kwargs={'pk': order.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], order.id)
        self.assertEqual(response.data['buyer'], self.buyer.id)
        self.assertEqual(len(response.data['items']), 1)
    
    def test_update_order_status(self):
        """Test la mise à jour du statut d'une commande"""
        order = Order.objects.create(
            buyer=self.buyer,
            farmer=self.farmer,
            shipping_address='Test Address',
            total_amount=10.00
        )
        
        # S'authentifier en tant que farmer (propriétaire de la commande)
        refresh = RefreshToken.for_user(self.farmer)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('order-detail', kwargs={'pk': order.id})
        data = {'status': 'confirmed'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'confirmed')
        
        # Vérifier en base de données
        order.refresh_from_db()
        self.assertEqual(order.status, 'confirmed')
    
    def test_order_history(self):
        """Test la récupération de l'historique des commandes"""
        # Créer plusieurs commandes
        for i in range(3):
            Order.objects.create(
                buyer=self.buyer,
                farmer=self.farmer,
                shipping_address=f'Address {i}',
                total_amount=10.00 + i,
                status='delivered' if i % 2 == 0 else 'pending'
            )
        
        url = reverse('order-history')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        
        # Tester le filtrage par statut
        response = self.client.get(url + '?status=delivered')
        self.assertEqual(len(response.data), 2)  # 2 commandes delivered
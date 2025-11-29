from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .test_setup import OrderTestSetup
from orders.models import Order, OrderItem, Cart, CartItem
from decimal import Decimal

class IntegrationTests(OrderTestSetup):
    
    def test_complete_order_flow(self):
        """Test le flux complet de commande"""
        # 1. Ajouter au panier
        add_url = reverse('add-to-cart')
        self.client.post(add_url, {'product': self.product1.id, 'quantity': 2}, format='json')
        
        # 2. Vérifier le panier
        cart_url = reverse('cart-detail')
        cart_response = self.client.get(cart_url)
        self.assertEqual(cart_response.data['total_items'], 2)
        
        # 3. Créer la commande - utiliser Decimal pour delivery_fee
        order_url = reverse('order-list')
        order_data = {
            'shipping_address': '123 Test Street',
            'delivery_fee': '5.00'  # ENVOYER COMME STRING POUR DECIMAL
        }
        order_response = self.client.post(order_url, order_data, format='json')
        
        # Vérifier que la commande a été créée
        if order_response.status_code != status.HTTP_201_CREATED:
            print("Erreur création commande:", order_response.data)  # Pour debug
        
        self.assertEqual(order_response.status_code, status.HTTP_201_CREATED)
        
        # 4. Vérifier que le panier est vide
        cart_response_after = self.client.get(cart_url)
        self.assertEqual(cart_response_after.data['total_items'], 0)
        
        # 5. Farmer confirme la commande
        refresh = RefreshToken.for_user(self.farmer)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        update_url = reverse('order-detail', kwargs={'pk': order_response.data['id']})
        update_response = self.client.patch(update_url, {'status': 'confirmed'}, format='json')
        
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        
        # 6. Vérifier le statut mis à jour
        order_detail = self.client.get(update_url)
        self.assertEqual(order_detail.data['status'], 'confirmed')
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from .test_setup import OrderTestSetup
from orders.models import Cart, CartItem

class CartTests(OrderTestSetup):
    
    def test_get_cart(self):
        """Test la récupération du panier"""
        url = reverse('cart-detail')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.buyer.id)
        self.assertEqual(len(response.data['items']), 0)
    
    def test_add_to_cart(self):
        """Test l'ajout d'un produit au panier"""
        url = reverse('add-to-cart')
        data = {
            'product': self.product1.id,
            'quantity': 3
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['product'], self.product1.id)
        self.assertEqual(response.data['quantity'], 3)
        
        # Vérifier que l'item est bien dans le panier
        cart_item = CartItem.objects.get(cart__user=self.buyer, product=self.product1)
        self.assertEqual(cart_item.quantity, 3)
    
    def test_add_to_cart_existing_item(self):
        """Test l'ajout d'un produit déjà présent dans le panier"""
        # Ajouter d'abord le produit
        CartItem.objects.create(
            cart=self.cart,
            product=self.product1,
            quantity=2
        )
        
        url = reverse('add-to-cart')
        data = {
            'product': self.product1.id,
            'quantity': 3
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Vérifier que la quantité a été augmentée
        cart_item = CartItem.objects.get(cart__user=self.buyer, product=self.product1)
        self.assertEqual(cart_item.quantity, 5)
    
    def test_update_cart_item(self):
        """Test la mise à jour d'un item du panier"""
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product1,
            quantity=2
        )
        
        url = reverse('update-cart-item', kwargs={'pk': cart_item.id})
        data = {'quantity': 5}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantity'], 5)
        
        # Vérifier en base de données
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 5)
    
    def test_remove_from_cart(self):
        """Test la suppression d'un item du panier"""
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product1,
            quantity=2
        )
        
        url = reverse('remove-cart-item', kwargs={'pk': cart_item.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CartItem.objects.filter(id=cart_item.id).exists())
    
    def test_cart_total_calculation(self):
        """Test le calcul du total du panier"""
        # Ajouter plusieurs items
        CartItem.objects.create(
            cart=self.cart,
            product=self.product1,
            quantity=2
        )
        CartItem.objects.create(
            cart=self.cart,
            product=self.product2,
            quantity=3
        )
        
        url = reverse('cart-detail')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_items'], 5)
        
        # Calcul attendu: (2 * 2.50) + (3 * 1.80) = 5.00 + 5.40 = 10.40
        expected_total = (2 * 2.50) + (3 * 1.80)
        self.assertEqual(float(response.data['total_price']), expected_total)
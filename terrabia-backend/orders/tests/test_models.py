from django.test import TestCase
from django.contrib.auth import get_user_model
from .test_setup import OrderTestSetup
from orders.models import Order, OrderItem, Cart, CartItem, Review

User = get_user_model()

class ModelTests(OrderTestSetup):
    
    def test_order_item_total_price(self):
        """Test le calcul du prix total d'un OrderItem"""
        order = Order.objects.create(
            buyer=self.buyer,
            farmer=self.farmer,
            shipping_address='Test',
            total_amount=25.00
        )
        
        order_item = OrderItem.objects.create(
            order=order,
            product=self.product1,
            quantity=4,
            unit_price=2.50
        )
        
        expected_total = 4 * 2.50
        self.assertEqual(order_item.total_price, expected_total)
    
    def test_cart_str_representation(self):
        """Test la représentation en string du panier"""
        cart = Cart.objects.get(user=self.buyer)
        self.assertEqual(str(cart), f"Panier de {self.buyer.username}")
    
    def test_order_str_representation(self):
        """Test la représentation en string d'une commande"""
        order = Order.objects.create(
            buyer=self.buyer,
            farmer=self.farmer,
            shipping_address='Test',
            total_amount=25.00
        )
        
        expected_str = f"Commande #{order.id} - {self.buyer.username}"
        self.assertEqual(str(order), expected_str)
    
    def test_review_str_representation(self):
        """Test la représentation en string d'un avis"""
        order = Order.objects.create(
            buyer=self.buyer,
            farmer=self.farmer,
            shipping_address='Test',
            total_amount=25.00
        )
        
        review = Review.objects.create(
            order=order,
            reviewer=self.buyer,
            reviewed_user=self.farmer,
            rating=5
        )
        
        expected_str = f"Avis de {self.buyer.username} pour {self.farmer.username}"
        self.assertEqual(str(review), expected_str)
    
    def test_review_unique_constraint(self):
        """Test la contrainte d'unicité sur les avis"""
        order = Order.objects.create(
            buyer=self.buyer,
            farmer=self.farmer,
            shipping_address='Test',
            total_amount=25.00
        )
        
        Review.objects.create(
            order=order,
            reviewer=self.buyer,
            reviewed_user=self.farmer,
            rating=5
        )
        
        # Tentative de créer un deuxième avis pour la même commande par le même reviewer
        with self.assertRaises(Exception):  # IntegrityError ou ValidationError
            Review.objects.create(
                order=order,
                reviewer=self.buyer,
                reviewed_user=self.farmer,
                rating=4
            )
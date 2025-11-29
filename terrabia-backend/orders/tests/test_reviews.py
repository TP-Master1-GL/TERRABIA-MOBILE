from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .test_setup import OrderTestSetup
from orders.models import Order, Review

class ReviewTests(OrderTestSetup):
    
    def setUp(self):
        super().setUp()
        # Créer une commande pour les tests d'avis
        self.order = Order.objects.create(
            buyer=self.buyer,
            farmer=self.farmer,
            shipping_address='Test Address',
            total_amount=10.00,
            status='delivered'  # IMPORTANT: doit être 'delivered' pour les avis
        )
    
    def test_create_review(self):
        """Test la création d'un avis"""
        url = reverse('review-create')
        data = {
            'order': self.order.id,
            'reviewed_user': self.farmer.id,
            'rating': 5,
            'comment': 'Excellent produit et service!'
        }
        # NE PAS INCLURE 'reviewer' - il sera défini automatiquement
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['rating'], 5)
        self.assertEqual(response.data['comment'], 'Excellent produit et service!')
        self.assertEqual(response.data['reviewer'], self.buyer.id)  # Doit être automatiquement défini
        
        # Vérifier en base de données
        review = Review.objects.get(order=self.order)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.reviewer, self.buyer)  # Vérifier que le reviewer est correct
    
    def test_create_duplicate_review(self):
        """Test la création d'un avis dupliqué pour la même commande"""
        Review.objects.create(
            order=self.order,
            reviewer=self.buyer,  # Définir explicitement le reviewer
            reviewed_user=self.farmer,
            rating=4,
            comment='Bon'
        )
        
        url = reverse('review-create')
        data = {
            'order': self.order.id,
            'reviewed_user': self.farmer.id,
            'rating': 5,
            'comment': 'Excellent'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_get_user_reviews(self):
        """Test la récupération des avis d'un utilisateur"""
        # Créer quelques avis
        Review.objects.create(
            order=self.order,
            reviewer=self.buyer,
            reviewed_user=self.farmer,
            rating=5,
            comment='Excellent'
        )
        
        # S'authentifier en tant que farmer (celui qui reçoit les avis)
        refresh = RefreshToken.for_user(self.farmer)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('user-reviews')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['rating'], 5)
        self.assertEqual(response.data[0]['reviewed_user'], self.farmer.id)
    
    def test_review_validation_rating_range(self):
        """Test la validation de la note (doit être entre 1 et 5)"""
        url = reverse('review-create')
        data = {
            'order': self.order.id,
            'reviewed_user': self.farmer.id,
            'rating': 6,  # Note invalide
            'comment': 'Test'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('rating', response.data)
    
    def test_review_validation_order_not_delivered(self):
        """Test qu'on ne peut pas noter une commande non livrée"""
        # Créer une commande non livrée
        pending_order = Order.objects.create(
            buyer=self.buyer,
            farmer=self.farmer,
            shipping_address='Test Address',
            total_amount=10.00,
            status='pending'  # Pas livrée
        )
        
        url = reverse('review-create')
        data = {
            'order': pending_order.id,
            'reviewed_user': self.farmer.id,
            'rating': 5,
            'comment': 'Test'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
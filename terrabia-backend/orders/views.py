from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db import transaction
from decimal import Decimal
from .models import Order, OrderItem, Cart, CartItem, Review
from .serializers import (OrderSerializer, CartSerializer, CartItemSerializer, 
                         ReviewSerializer, OrderItemSerializer)

class CartDetailView(generics.RetrieveAPIView):
    """
    🛒 Détails du panier
    
    Récupère le panier de l'utilisateur connecté avec tous les items et calculs automatiques.
    """
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart
    
    @swagger_auto_schema(
        operation_summary="Voir le panier",
        operation_description="""
        Récupère le panier complet de l'utilisateur connecté.
        
        ### Informations retournées :
        - Liste des items avec produits et quantités
        - Nombre total d'articles
        - Prix total du panier
        - Date de création et mise à jour
        
        🔒 **Authentification requise** - Chaque utilisateur a son propre panier.
        """,
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Token JWT : 'Bearer <votre_token>'",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: CartSerializer,
            401: openapi.Response(description="❌ Non authentifié")
        },
        tags=['🛒 Panier']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class AddToCartView(generics.CreateAPIView):
    """
    ➕ Ajouter au panier
    
    Ajoute un produit au panier de l'utilisateur connecté.
    Si le produit existe déjà, la quantité est augmentée.
    """
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Ajouter au panier",
        operation_description="""
        Ajoute un produit au panier de l'utilisateur connecté.
        
        ### Comportement :
        - Si le produit n'est pas dans le panier → Nouvel item créé
        - Si le produit existe déjà → Quantité augmentée
        - Vérification automatique du stock disponible
        
        ⚠️ **Limitations** :
        - Un produit ne peut être ajouté que par l'agriculteur qui le propose
        - La quantité ne peut pas dépasser le stock disponible
        
        🔒 **Authentification requise**
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['product', 'quantity'],
            properties={
                'product': openapi.Schema(
                    type=openapi.TYPE_INTEGER, 
                    description='ID du produit à ajouter'
                ),
                'quantity': openapi.Schema(
                    type=openapi.TYPE_INTEGER, 
                    description='Quantité à ajouter',
                    default=1,
                    minimum=1
                )
            }
        ),
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Token JWT : 'Bearer <votre_token>'",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            201: CartItemSerializer,
            400: openapi.Response(
                description="❌ Erreur de validation",
                examples={
                    "application/json": {
                        "product": ["Ce produit n'existe pas."],
                        "quantity": ["La quantité demandée dépasse le stock disponible."]
                    }
                }
            ),
            401: openapi.Response(description="❌ Non authentifié"),
            404: openapi.Response(description="❌ Produit non trouvé")
        },
        tags=['🛒 Panier']
    )
    def create(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product')
        quantity = int(request.data.get('quantity', 1))
        
        # Vérifier si le produit est déjà dans le panier
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_id=product_id,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        serializer = self.get_serializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UpdateCartItemView(generics.UpdateAPIView):
    """
    ✏️ Modifier un item du panier
    
    Met à jour la quantité d'un item spécifique dans le panier.
    """
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)
    
    @swagger_auto_schema(
        operation_summary="Modifier un item du panier",
        operation_description="""
        Met à jour la quantité d'un item spécifique dans le panier.
        
        ### Cas particuliers :
        - Si quantité = 0 → L'item est supprimé automatiquement
        - Si quantité > stock → Erreur de validation
        
        🔒 **Authentification requise** - Vous ne pouvez modifier que votre propre panier.
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['quantity'],
            properties={
                'quantity': openapi.Schema(
                    type=openapi.TYPE_INTEGER, 
                    description='Nouvelle quantité',
                    minimum=0
                )
            }
        ),
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Token JWT : 'Bearer <votre_token>'",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="ID de l'item du panier à modifier",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: CartItemSerializer,
            400: openapi.Response(description="❌ Données invalides"),
            401: openapi.Response(description="❌ Non authentifié"),
            404: openapi.Response(description="❌ Item non trouvé")
        },
        tags=['🛒 Panier']
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

class RemoveFromCartView(generics.DestroyAPIView):
    """
    🗑️ Supprimer du panier
    
    Supprime définitivement un item du panier.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)
    
    @swagger_auto_schema(
        operation_summary="Supprimer du panier",
        operation_description="""
        Supprime définitivement un item du panier.
        
        🔒 **Authentification requise** - Vous ne pouvez supprimer que les items de votre propre panier.
        """,
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Token JWT : 'Bearer <votre_token>'",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="ID de l'item du panier à supprimer",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            204: openapi.Response(description="✅ Item supprimé avec succès"),
            401: openapi.Response(description="❌ Non authentifié"),
            404: openapi.Response(description="❌ Item non trouvé")
        },
        tags=['🛒 Panier']
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

class OrderListView(generics.ListCreateAPIView):
    """
    📦 Gestion des commandes
    
    Liste les commandes de l'utilisateur ou crée une nouvelle commande depuis le panier.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'buyer':
            return Order.objects.filter(buyer=user)
        elif user.user_type == 'farmer':
            return Order.objects.filter(farmer=user)
        elif user.user_type == 'delivery':
            return Order.objects.filter(delivery_agent=user)
        return Order.objects.none()
    
    @swagger_auto_schema(
        operation_summary="Liste des commandes",
        operation_description="""
        Récupère la liste des commandes selon le type d'utilisateur :
        
        - **Acheteur** → Ses propres commandes
        - **Agriculteur** → Commandes de ses produits
        - **Livreur** → Commandes qui lui sont assignées
        
        ### Filtrage disponible :
        - `status` : Filtrer par statut de commande
        - `farmer` : Filtrer par agriculteur (acheteurs seulement)
        
        🔒 **Authentification requise**
        """,
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Token JWT : 'Bearer <votre_token>'",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description="Filtrer par statut",
                type=openapi.TYPE_STRING,
                enum=['pending', 'confirmed', 'preparing', 'ready', 'shipped', 'delivered', 'cancelled']
            ),
            openapi.Parameter(
                'farmer',
                openapi.IN_QUERY,
                description="Filtrer par agriculteur (ID)",
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={
            200: OrderSerializer(many=True),
            401: openapi.Response(description="❌ Non authentifié")
        },
        tags=['📦 Commandes']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Créer une commande",
        operation_description="""
        Crée une nouvelle commande à partir du panier de l'utilisateur.
        
        ### Processus :
        1. Vérification que le panier n'est pas vide
        2. Création de la commande avec les items du panier
        3. Calcul automatique du total (produits + frais de livraison)
        4. Vidage automatique du panier
        5. Notification à l'agriculteur
        
        ⚠️ **Pré-requis** :
        - Le panier ne doit pas être vide
        - Adresse de livraison obligatoire
        
        🔒 **Authentification requise** - Seuls les acheteurs peuvent créer des commandes.
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['shipping_address'],
            properties={
                'shipping_address': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Adresse complète de livraison'
                ),
                'delivery_fee': openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description='Frais de livraison',
                    default=0,
                    minimum=0
                ),
                'notes': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Instructions spéciales pour la livraison'
                )
            }
        ),
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Token JWT : 'Bearer <votre_token>'",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            201: OrderSerializer,
            400: openapi.Response(
                description="❌ Erreur de création",
                examples={
                    "application/json": {
                        "error": "Le panier est vide",
                        "shipping_address": ["Ce champ est obligatoire."]
                    }
                }
            ),
            401: openapi.Response(description="❌ Non authentifié"),
            403: openapi.Response(description="❌ Réservé aux acheteurs")
        },
        tags=['📦 Commandes']
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        cart = Cart.objects.get(user=request.user)
        if not cart.items.exists():
            return Response(
                {'error': 'Le panier est vide'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Créer la commande
        order_data = {
            'buyer': request.user,
            'shipping_address': request.data.get('shipping_address'),
            'delivery_fee': Decimal(request.data.get('delivery_fee', 0)),
        }
        
        # Déterminer le farmer (premier produit du panier)
        first_item = cart.items.first()
        order_data['farmer'] = first_item.product.farmer
        
        order = Order.objects.create(**order_data)
        
        # Créer les OrderItems
        total_amount = Decimal('0.00')
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                unit_price=cart_item.product.price
            )
            total_amount += cart_item.quantity * cart_item.product.price
        
        order.total_amount = total_amount + order.delivery_fee
        order.save()
        
        # Vider le panier
        cart.items.all().delete()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class OrderDetailView(generics.RetrieveUpdateAPIView):
    """
    📄 Détails d'une commande
    
    Récupère ou met à jour une commande spécifique.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'buyer':
            return Order.objects.filter(buyer=user)
        elif user.user_type == 'farmer':
            return Order.objects.filter(farmer=user)
        elif user.user_type == 'delivery':
            return Order.objects.filter(delivery_agent=user)
        return Order.objects.none()
    
    @swagger_auto_schema(
        operation_summary="Détails d'une commande",
        operation_description="""
        Récupère les détails complets d'une commande spécifique.
        
        ### Informations incluses :
        - Informations de la commande (statut, total, dates)
        - Liste des produits avec quantités et prix
        - Informations de l'acheteur et de l'agriculteur
        - Informations du livreur (si assigné)
        
        🔒 **Authentification requise** - Vous ne pouvez voir que vos commandes ou celles qui vous concernent.
        """,
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Token JWT : 'Bearer <votre_token>'",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="ID de la commande",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            200: OrderSerializer,
            401: openapi.Response(description="❌ Non authentifié"),
            404: openapi.Response(description="❌ Commande non trouvée")
        },
        tags=['📦 Commandes']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Mettre à jour une commande",
        operation_description="""
        Met à jour une commande (principalement le statut).
        
        ### Permissions par type d'utilisateur :
        - **Acheteur** : Peut annuler (`cancelled`) les commandes `pending`
        - **Agriculteur** : Peut mettre à jour tous les statuts sauf `delivered`
        - **Livreur** : Peut mettre à jour `shipped` → `delivered`
        
        🔒 **Authentification requise**
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Nouveau statut',
                    enum=['pending', 'confirmed', 'preparing', 'ready', 'shipped', 'delivered', 'cancelled']
                ),
                'delivery_agent': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='ID du livreur à assigner (agriculteur seulement)'
                )
            }
        ),
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Token JWT : 'Bearer <votre_token>'",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: OrderSerializer,
            400: openapi.Response(description="❌ Données invalides"),
            401: openapi.Response(description="❌ Non authentifié"),
            403: openapi.Response(description="❌ Non autorisé"),
            404: openapi.Response(description="❌ Commande non trouvée")
        },
        tags=['📦 Commandes']
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

class OrderHistoryView(generics.ListAPIView):
    """
    📊 Historique des commandes
    
    Récupère l'historique des commandes avec filtrage par statut.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        status_filter = self.request.query_params.get('status', None)
        
        queryset = Order.objects.filter(buyer=user)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')
    
    @swagger_auto_schema(
        operation_summary="Historique des commandes",
        operation_description="""
        Récupère l'historique des commandes de l'utilisateur connecté (acheteur).
        
        ### Utilisation typique :
        - Voir toutes les commandes passées
        - Filtrer par statut (ex: voir seulement les commandes livrées)
        - Suivre l'évolution des commandes
        
        🔒 **Authentification requise** - Réservé aux acheteurs.
        """,
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Token JWT : 'Bearer <votre_token>'",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description="Filtrer par statut",
                type=openapi.TYPE_STRING,
                enum=['pending', 'confirmed', 'preparing', 'ready', 'shipped', 'delivered', 'cancelled']
            )
        ],
        responses={
            200: OrderSerializer(many=True),
            401: openapi.Response(description="❌ Non authentifié"),
            403: openapi.Response(description="❌ Réservé aux acheteurs")
        },
        tags=['📦 Commandes']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class ReviewCreateView(generics.CreateAPIView):
    """
    ⭐ Créer un avis
    
    Ajoute un avis et une note pour une commande livrée.
    """
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Créer un avis",
        operation_description="""
        Crée un avis pour une commande livrée.
        
        ### Conditions :
        - La commande doit avoir le statut `delivered`
        - L'utilisateur doit être l'acheteur ou l'agriculteur de la commande
        - Un seul avis par commande par utilisateur
        
        ### Utilisation :
        - Acheteur → Note l'agriculteur et les produits
        - Agriculteur → Note l'acheteur
        
        🔒 **Authentification requise**
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['order', 'reviewed_user', 'rating'],
            properties={
                'order': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='ID de la commande livrée'
                ),
                'reviewed_user': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='ID de l\'utilisateur à noter'
                ),
                'rating': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='Note de 1 à 5 étoiles',
                    enum=[1, 2, 3, 4, 5]
                ),
                'comment': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Commentaire (optionnel)',
                    maxLength=500
                )
            }
        ),
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Token JWT : 'Bearer <votre_token>'",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            201: ReviewSerializer,
            400: openapi.Response(
                description="❌ Erreur de validation",
                examples={
                    "application/json": {
                        "non_field_errors": ["Vous ne pouvez laisser un avis que pour les commandes livrées."],
                        "rating": ["La note doit être entre 1 et 5."]
                    }
                }
            ),
            401: openapi.Response(description="❌ Non authentifié")
        },
        tags=['⭐ Avis']
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

class UserReviewsView(generics.ListAPIView):
    """
    📝 Mes avis reçus
    
    Liste tous les avis reçus par l'utilisateur connecté.
    """
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Review.objects.filter(reviewed_user=self.request.user)
    
    @swagger_auto_schema(
        operation_summary="Avis reçus",
        operation_description="""
        Récupère tous les avis que l'utilisateur connecté a reçus.
        
        ### Informations incluses :
        - Note et commentaire
        - Informations de l'utilisateur qui a noté
        - Commande associée
        - Date de l'avis
        
        🔒 **Authentification requise**
        """,
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Token JWT : 'Bearer <votre_token>'",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: ReviewSerializer(many=True),
            401: openapi.Response(description="❌ Non authentifié")
        },
        tags=['⭐ Avis']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login
from .models import User, FarmerProfile, BuyerProfile, DeliveryProfile
from .serializers import (UserRegistrationSerializer, UserLoginSerializer, 
                         UserSerializer, FarmerProfileSerializer, 
                         BuyerProfileSerializer, DeliveryProfileSerializer)

class UserRegistrationView(generics.CreateAPIView):
    """
    📝 Inscription d'un nouvel utilisateur
    
    Crée un nouveau compte utilisateur avec le type spécifié (farmer, buyer, delivery).
    Retourne les tokens JWT après l'inscription réussie.
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_summary="Inscription utilisateur",
        operation_description="""
        Crée un nouveau compte utilisateur avec le profil correspondant.
        
        ### Types d'utilisateurs supportés :
        - **farmer** : Agriculteur (crée un FarmerProfile)
        - **buyer** : Acheteur (crée un BuyerProfile) 
        - **delivery** : Service de livraison (crée un DeliveryProfile)
        
        ⚠️ Les mots de passe doivent correspondre et faire au moins 6 caractères.
        """,
        request_body=UserRegistrationSerializer,
        responses={
            201: openapi.Response(
                description="✅ Inscription réussie",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            description='Informations de l\'utilisateur créé'
                        ),
                        'refresh': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Token de rafraîchissement JWT'
                        ),
                        'access': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Token d\'accès JWT'
                        ),
                    }
                ),
                examples={
                    "application/json": {
                        "user": {
                            "id": 1,
                            "username": "jean_agriculteur",
                            "email": "jean@ferme.com",
                            "user_type": "farmer",
                            "phone_number": "+33612345678",
                            "first_name": "Jean",
                            "last_name": "Dupont",
                            "is_verified": False
                        },
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                    }
                }
            ),
            400: openapi.Response(
                description="❌ Erreur de validation",
                examples={
                    "application/json": {
                        "username": ["Ce nom d'utilisateur est déjà pris."],
                        "password": ["Les mots de passe ne correspondent pas."],
                        "email": ["Cette adresse email est déjà utilisée."]
                    }
                }
            )
        },
        tags=['👥 Authentification']
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Créer le profil spécifique selon le type d'utilisateur
        user_type = user.user_type
        try:
            if user_type == 'farmer':
                FarmerProfile.objects.create(user=user)
            elif user_type == 'buyer':
                BuyerProfile.objects.create(user=user)
            elif user_type == 'delivery':
                DeliveryProfile.objects.create(user=user)
        except Exception as e:
            user.delete()
            return Response(
                {'error': f'Erreur lors de la création du profil: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

class UserLoginView(generics.GenericAPIView):
    """
    🔐 Connexion utilisateur
    
    Authentifie un utilisateur avec son username/email et mot de passe.
    Retourne les tokens JWT pour les requêtes suivantes.
    """
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_summary="Connexion utilisateur",
        operation_description="""
        Authentifie un utilisateur existant et retourne les tokens JWT.
        
        ### Identifiants acceptés :
        - **Username** ou **Email**
        - **Mot de passe**
        
        🔒 Les tokens sont valables 24h (access) et 7 jours (refresh).
        """,
        request_body=UserLoginSerializer,
        responses={
            200: openapi.Response(
                description="✅ Connexion réussie",
                examples={
                    "application/json": {
                        "user": {
                            "id": 1,
                            "username": "jean_agriculteur",
                            "email": "jean@ferme.com",
                            "user_type": "farmer",
                            "first_name": "Jean",
                            "last_name": "Dupont"
                        },
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                    }
                }
            ),
            400: openapi.Response(
                description="❌ Identifiants invalides",
                examples={
                    "application/json": {
                        "non_field_errors": ["Identifiants invalides"]
                    }
                }
            )
        },
        tags=['👥 Authentification']
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

class UserListView(generics.ListAPIView):
    """
    📋 Liste des utilisateurs
    
    Retourne la liste de tous les utilisateurs inscrits sur la plateforme.
    Requiert une authentification.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="Liste des utilisateurs",
        operation_description="""
        Récupère la liste complète des utilisateurs de la plateforme.
        
        🔒 **Authentification requise** - Seuls les utilisateurs connectés peuvent accéder à cette ressource.
        
        ### Filtrage possible via query parameters :
        - `user_type` : Filtrer par type (farmer, buyer, delivery)
        - `search` : Recherche textuelle sur username, email, nom, prénom
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
                'user_type',
                openapi.IN_QUERY,
                description="Filtrer par type d'utilisateur",
                type=openapi.TYPE_STRING,
                enum=['farmer', 'buyer', 'delivery']
            ),
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Recherche textuelle (username, email, nom, prénom)",
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: UserSerializer(many=True),
            401: openapi.Response(description="❌ Non authentifié - Token manquant ou invalide"),
            403: openapi.Response(description="❌ Accès refusé - Permissions insuffisantes")
        },
        tags=['👥 Utilisateurs']
    )
    def get(self, request, *args, **kwargs):
        # Implémentation du filtrage
        from django.db import models  # AJOUTER CET IMPORT
        user_type = request.query_params.get('user_type')
        search = request.query_params.get('search')
        
        queryset = self.get_queryset()
        
        if user_type:
            queryset = queryset.filter(user_type=user_type)
        
        if search:
            queryset = queryset.filter(
                models.Q(username__icontains=search) |
                models.Q(email__icontains=search) |
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search)
            )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    👤 Gestion d'un utilisateur
    
    Récupère, met à jour ou supprime un utilisateur spécifique.
    Utilisez 'me' pour cibler l'utilisateur connecté.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        if self.kwargs.get('pk') == 'me':
            return self.request.user
        return super().get_object()
    
    @swagger_auto_schema(
        operation_summary="Détails d'un utilisateur",
        operation_description="""
        Récupère les informations détaillées d'un utilisateur spécifique.
        
        ### Utilisation spéciale :
        - Utilisez `me` comme ID pour récupérer l'utilisateur connecté
        - Exemple : `/api/auth/users/me/`
        
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
                'pk',
                openapi.IN_PATH,
                description="ID de l'utilisateur ou 'me' pour l'utilisateur courant",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: UserSerializer,
            404: openapi.Response(description="❌ Utilisateur non trouvé"),
            401: openapi.Response(description="❌ Non authentifié")
        },
        tags=['👥 Utilisateurs']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Mettre à jour un utilisateur",
        operation_description="""
        Met à jour partiellement les informations d'un utilisateur.
        
        ⚠️ **Note** : Certains champs comme `user_type` ne peuvent pas être modifiés après l'inscription.
        
        🔒 **Authentification requise** - Vous ne pouvez modifier que votre propre profil.
        """,
        request_body=UserSerializer,
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
            200: UserSerializer,
            400: openapi.Response(description="❌ Données invalides"),
            401: openapi.Response(description="❌ Non authentifié"),
            403: openapi.Response(description="❌ Non autorisé - Vous ne pouvez modifier que votre profil")
        },
        tags=['👥 Utilisateurs']
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Supprimer un utilisateur",
        operation_description="""
        Supprime définitivement un compte utilisateur.
        
        ⚠️ **Action irréversible** - Toutes les données associées seront perdues.
        
        🔒 **Authentification requise** - Vous ne pouvez supprimer que votre propre compte.
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
            204: openapi.Response(description="✅ Utilisateur supprimé avec succès"),
            401: openapi.Response(description="❌ Non authentifié"),
            403: openapi.Response(description="❌ Non autorisé"),
            404: openapi.Response(description="❌ Utilisateur non trouvé")
        },
        tags=['👥 Utilisateurs']
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

class FarmerProfileView(generics.RetrieveUpdateAPIView):
    """
    🚜 Profil agriculteur
    
    Gestion du profil spécifique aux agriculteurs.
    """
    serializer_class = FarmerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user.farmer_profile
    
    @swagger_auto_schema(
        operation_summary="Profil agriculteur",
        operation_description="""
        Récupère le profil agriculteur de l'utilisateur connecté.
        
        ### Informations incluses :
        - Nom de la ferme
        - Localisation
        - Superficie
        - Certifications
        - Description
        
        🔒 **Authentification requise** - Seuls les agriculteurs peuvent accéder à cette ressource.
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
            200: FarmerProfileSerializer,
            404: openapi.Response(description="❌ Profil agriculteur non trouvé - L'utilisateur n'est pas un agriculteur"),
            401: openapi.Response(description="❌ Non authentifié")
        },
        tags=['👥 Profils']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Mettre à jour le profil agriculteur",
        operation_description="""
        Met à jour les informations du profil agriculteur.
        
        🔒 **Authentification requise** - Seuls les agriculteurs peuvent modifier leur profil.
        """,
        request_body=FarmerProfileSerializer,
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
            200: FarmerProfileSerializer,
            400: openapi.Response(description="❌ Données invalides"),
            401: openapi.Response(description="❌ Non authentifié"),
            404: openapi.Response(description="❌ Profil non trouvé")
        },
        tags=['👥 Profils']
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

class BuyerProfileView(generics.RetrieveUpdateAPIView):
    """
    🛒 Profil acheteur
    
    Gestion du profil spécifique aux acheteurs.
    """
    serializer_class = BuyerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user.buyer_profile
    
    @swagger_auto_schema(
        operation_summary="Profil acheteur",
        operation_description="""
        Récupère le profil acheteur de l'utilisateur connecté.
        
        ### Informations incluses :
        - Nom de l'entreprise
        - Type de business
        - Préférences d'achat
        
        🔒 **Authentification requise** - Seuls les acheteurs peuvent accéder à cette ressource.
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
            200: BuyerProfileSerializer,
            404: openapi.Response(description="❌ Profil acheteur non trouvé - L'utilisateur n'est pas un acheteur"),
            401: openapi.Response(description="❌ Non authentifié")
        },
        tags=['👥 Profils']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Mettre à jour le profil acheteur",
        operation_description="""
        Met à jour les informations du profil acheteur.
        
        🔒 **Authentification requise** - Seuls les acheteurs peuvent modifier leur profil.
        """,
        request_body=BuyerProfileSerializer,
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
            200: BuyerProfileSerializer,
            400: openapi.Response(description="❌ Données invalides"),
            401: openapi.Response(description="❌ Non authentifié")
        },
        tags=['👥 Profils']
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

class DeliveryProfileView(generics.RetrieveUpdateAPIView):
    """
    🚚 Profil livreur
    
    Gestion du profil spécifique aux services de livraison.
    """
    serializer_class = DeliveryProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user.delivery_profile
    
    @swagger_auto_schema(
        operation_summary="Profil livreur",
        operation_description="""
        Récupère le profil livreur de l'utilisateur connecté.
        
        ### Informations incluses :
        - Nom de l'entreprise
        - Numéro de licence
        - Type de véhicule
        - Zones de livraison
        - Note moyenne
        
        🔒 **Authentification requise** - Seuls les livreurs peuvent accéder à cette ressource.
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
            200: DeliveryProfileSerializer,
            404: openapi.Response(description="❌ Profil livreur non trouvé - L'utilisateur n'est pas un livreur"),
            401: openapi.Response(description="❌ Non authentifié")
        },
        tags=['👥 Profils']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Mettre à jour le profil livreur",
        operation_description="""
        Met à jour les informations du profil livreur.
        
        🔒 **Authentification requise** - Seuls les livreurs peuvent modifier leur profil.
        """,
        request_body=DeliveryProfileSerializer,
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
            200: DeliveryProfileSerializer,
            400: openapi.Response(description="❌ Données invalides"),
            401: openapi.Response(description="❌ Non authentifié")
        },
        tags=['👥 Profils']
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

# Vue pour la vérification du token
@swagger_auto_schema(
    method='get',
    operation_summary="Vérifier l'authentification",
    operation_description="""
    Vérifie si le token JWT est valide et retourne les informations de l'utilisateur connecté.
    
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
        200: UserSerializer,
        401: openapi.Response(description="❌ Token invalide ou expiré")
    },
    tags=['👥 Authentification']
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def verify_token(request):
    """
    ✅ Vérification du token JWT
    
    Endpoint utilitaire pour vérifier la validité du token et récupérer les informations utilisateur.
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
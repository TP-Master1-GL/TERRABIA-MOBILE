# Terrabia/swagger.py
from django.urls import path, include  # ← AJOUTÉ ICI !
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
             title="Terrabia API",
        default_version='v1',
        description="""
        # 🚀 API Terrabia - Documentation Complète
        
        Plateforme de mise en relation entre agriculteurs et acheteurs pour une distribution optimale des produits agricoles.
        
        ## 📋 Fonctionnalités Principales
        
        - **👥 Gestion des utilisateurs** : Inscription, authentification, profils (agriculteurs, acheteurs, livreurs)
        - **🛒 Gestion des produits** : Catalogue, catégories, images
        - **📦 Gestion des commandes** : Panier, commandes, historique, statuts
        - **⭐ Système de notation** : Avis et commentaires
        - **💬 Messagerie** : Chat en temps réel entre utilisateurs
        - **🔐 Authentification JWT** : Sécurisée avec refresh token
        
        ## 🔐 Authentification
        
        L'API utilise l'authentification JWT. Pour utiliser les endpoints protégés :
        
        ```http
        Authorization: Bearer <votre_access_token>
        ```
        
        ### Processus d'authentification :
        1. **Inscription** → `/api/auth/register/`
        2. **Connexion** → `/api/auth/login/` ou `/api/token/`
        3. **Utiliser le token** dans le header Authorization
        4. **Rafraîchir le token** → `/api/token/refresh/`
        
        ## 👥 Types d'Utilisateurs
        
        | Type | Description | Permissions |
        |------|-------------|-------------|
        | `farmer` | Agriculteur | Peut créer des produits, gérer ses commandes |
        | `buyer` | Acheteur | Peut acheter des produits, noter les commandes |
        | `delivery` | Livreur | Peut être assigné aux commandes pour livraison |
        
        ## 📊 Statuts des Commandes
        
        `pending` → `confirmed` → `preparing` → `ready` → `shipped` → `delivered`
        
        *Les avis ne sont possibles que sur les commandes `delivered`.*
        """,
        contact=openapi.Contact(email="contact@terrabia.com"),
        license=openapi.License(name="Terrabia 2025"),
    ),
        
   
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]
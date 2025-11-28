# Terrabia/swagger.py
from django.urls import path, include  # ← AJOUTÉ ICI !
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Terrabia API - Marketplace Agricole",
        default_version='v1',
        description="""
        API complète de Terrabia - Marketplace agricole locale
        
        Fonctionnalités actuelles :
        • Authentification JWT
        • Chat en temps réel (WebSocket + REST API)
        • Conversations sécurisées entre utilisateurs
        
        Prochaines étapes :
        • Produits & catégories
        • Panier & commandes
        • Paiement mobile money
        • Livraison géolocalisée
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
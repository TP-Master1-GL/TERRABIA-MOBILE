# Terrabia/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Chat API
    path('api/chat/', include('chat.urls')),

    # Products API
    path('api/products/', include('products.urls')),
    
    # Users API
    path('api/auth/', include('users.urls')),
        
    # Documentation Swagger & ReDoc
    path('', include('Terrabia.swagger')),  # ← Met la doc en racine
]
# Pour servir les images en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


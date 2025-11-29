from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # 🔐 Authentification
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('verify/', views.verify_token, name='verify-token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # 👥 Gestion des utilisateurs
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('users/me/', views.UserDetailView.as_view(), name='user-me'),
    
    # 📋 Gestion des profils
    path('profile/farmer/', views.FarmerProfileView.as_view(), name='farmer-profile'),
    path('profile/buyer/', views.BuyerProfileView.as_view(), name='buyer-profile'),
    path('profile/delivery/', views.DeliveryProfileView.as_view(), name='delivery-profile'),
]
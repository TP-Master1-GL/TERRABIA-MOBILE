from django.urls import path
from . import views

urlpatterns = [
    # 🛒 Gestion du panier
    path('cart/', views.CartDetailView.as_view(), name='cart-detail'),
    path('cart/add/', views.AddToCartView.as_view(), name='add-to-cart'),
    path('cart/items/<int:pk>/', views.UpdateCartItemView.as_view(), name='update-cart-item'),
    path('cart/items/<int:pk>/remove/', views.RemoveFromCartView.as_view(), name='remove-cart-item'),
    
    # 📦 Gestion des commandes
    path('orders/', views.OrderListView.as_view(), name='order-list'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('orders/history/', views.OrderHistoryView.as_view(), name='order-history'),
    
    # ⭐ Gestion des avis
    path('reviews/', views.ReviewCreateView.as_view(), name='review-create'),
    path('reviews/my/', views.UserReviewsView.as_view(), name='user-reviews'),
]
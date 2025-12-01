# products/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Catégories
    path('categories/', views.CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),
    
    # Produits
    path('products/', views.ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    
    # Produits du farmer connecté
    path('my-products/', views.my_products, name='my-products'),
    
    # Favoris
    path('favorites/', views.favorites, name='favorites'),
    path('products/<int:product_id>/toggle_favorite/', views.toggle_favorite, name='toggle-favorite'),
]

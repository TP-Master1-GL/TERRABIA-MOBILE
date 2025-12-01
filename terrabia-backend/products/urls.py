# products/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Catégories - URLs modifiées
    path('categories/', views.CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),
    
    # Produits - URLs inchangées
    path('products/', views.ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('favorites/', ProductViewSet.as_view({'get': 'favorites'}), name='favorites'),
    path('my-products/', views.my_products, name='my-products'), 
    
]

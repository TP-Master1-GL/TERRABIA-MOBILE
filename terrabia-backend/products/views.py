# products/views.py
from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, BasePermission
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer

# Permission personnalisée : seul le farmer peut modifier ses produits
class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return obj.farmer == request.user

# Permission personnalisée pour les catégories
class CanCreateCategoryOrReadOnly(BasePermission):
    """
    Permission personnalisée :
    - Lecture : Autorisé à tous
    - Création : Admins et agriculteurs
    - Modification/Suppression : Admins seulement
    """
    def has_permission(self, request, view):
        # GET, HEAD, OPTIONS autorisés à tous
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # POST : seulement admins et agriculteurs
        if request.method == 'POST':
            return request.user.is_authenticated and (
                request.user.is_staff or 
                request.user.is_superuser or 
                request.user.user_type == 'farmer'
            )
        
        return False
    
    def has_object_permission(self, request, view, obj):
        # GET, HEAD, OPTIONS autorisés à tous
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # PUT, PATCH, DELETE : seulement admins
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user.is_authenticated and (
                request.user.is_staff or 
                request.user.is_superuser
            )
        
        return False

# Catégories - MODIFIÉ
class CategoryListCreateView(generics.ListCreateAPIView):  # Changé de ListAPIView à ListCreateAPIView
    queryset = Category.objects.filter(parent=None)
    serializer_class = CategorySerializer
    permission_classes = [CanCreateCategoryOrReadOnly]  # Nouvelle permission

# Vue pour modifier/supprimer les catégories (admin seulement)
class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [CanCreateCategoryOrReadOnly]

# Produits (inchangé)
class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.filter(available=True)
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'unit']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']

    def perform_create(self, serializer):
        serializer.save(farmer=self.request.user)

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsOwnerOrReadOnly]
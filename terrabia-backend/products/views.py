# products/views.py
from rest_framework import generics, filters, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404

# Permission personnalisée : seul le farmer peut modifier ses produits
class IsOwnerOrReadOnly(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        # Lecture autorisée à tous
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # Écriture: seulement le propriétaire
        return obj.farmer == request.user

# Catégories
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.filter(parent=None)
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

# Produits
class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.filter(available=True)
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'unit']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']

    def perform_create(self, serializer):
        # Associer automatiquement le farmer connecté
        serializer.save(farmer=self.request.user)

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsOwnerOrReadOnly]

# Vue pour récupérer les produits du farmer connecté
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_products(request):
    products = Product.objects.filter(farmer=request.user)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

# Vue pour les favoris
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def favorites(request):
    favorite_products = request.user.favorite_products.all()
    serializer = ProductSerializer(favorite_products, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.user in product.favorited_by.all():
        product.favorited_by.remove(request.user)
        is_favorite = False
    else:
        product.favorited_by.add(request.user)
        is_favorite = True
    
    return Response({
        'success': True,
        'is_favorite': is_favorite,
        'product_id': product_id
    })# products/views.py
from rest_framework import generics, filters, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404

# Permission personnalisée : seul le farmer peut modifier ses produits
class IsOwnerOrReadOnly(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        # Lecture autorisée à tous
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # Écriture: seulement le propriétaire
        return obj.farmer == request.user

# Catégories
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.filter(parent=None)
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

# Produits
class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.filter(available=True)
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'unit']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']

    def perform_create(self, serializer):
        # Associer automatiquement le farmer connecté
        serializer.save(farmer=self.request.user)

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsOwnerOrReadOnly]

# Vue pour récupérer les produits du farmer connecté
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_products(request):
    products = Product.objects.filter(farmer=request.user)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

# Vue pour les favoris
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def favorites(request):
    favorite_products = request.user.favorite_products.all()
    serializer = ProductSerializer(favorite_products, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.user in product.favorited_by.all():
        product.favorited_by.remove(request.user)
        is_favorite = False
    else:
        product.favorited_by.add(request.user)
        is_favorite = True
    
    return Response({
        'success': True,
        'is_favorite': is_favorite,
        'product_id': product_id
    })

# products/views.py
from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer

# Custom permission: seul le farmer peut modifier ses produits
from rest_framework.permissions import BasePermission

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return obj.farmer == request.user

# Catégories
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.filter(parent=None)
    serializer_class = CategorySerializer

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
        serializer.save(farmer=self.request.user)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsOwnerOrReadOnly]
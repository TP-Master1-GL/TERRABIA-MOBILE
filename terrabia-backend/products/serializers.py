# products/serializers.py
from rest_framework import serializers
from .models import Category, Product, ProductImage
from django.contrib.auth import get_user_model
from users.serializers import UserSerializer

User = get_user_model()

# Serializer minimal pour l'agriculteur (farmer)
class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image', 'parent', 'subcategories']

    def get_subcategories(self, obj):
        return CategorySerializer(obj.subcategories.all(), many=True).data


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_main']


class ProductSerializer(serializers.ModelSerializer):
    farmer = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model = Product
        fields = [
            'id', 'farmer', 'category', 'category_id', 'name', 'slug',
            'description', 'price', 'unit', 'stock', 'available',
            'created_at', 'updated_at', 'images', 'uploaded_images'
        ]

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        product = Product.objects.create(**validated_data)
        
        for i, image in enumerate(uploaded_images):
            ProductImage.objects.create(
                product=product,
                image=image,
                is_main=(i == 0)  # la première image est principale
            )
        return product
# products/serializers.py
from rest_framework import serializers
from .models import Category, Product, ProductImage
from django.contrib.auth import get_user_model

User = get_user_model()

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
    farmer = SimpleUserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    
    # Correction: utiliser 'images' pour l'upload au lieu de 'uploaded_images'
    images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )

    class Meta:
        model = Product
        fields = [
            'id', 'farmer', 'category', 'category_id', 'name', 'slug',
            'description', 'price', 'unit', 'stock', 'available',
            'created_at', 'updated_at', 'images', 'images'
        ]
        read_only_fields = ['farmer', 'slug']

    def create(self, validated_data):
        # Extraire les images
        images_data = validated_data.pop('images', [])
        
        # Créer le produit
        product = Product.objects.create(**validated_data)
        
        # Ajouter les images
        for i, image_data in enumerate(images_data):
            ProductImage.objects.create(
                product=product,
                image=image_data,
                is_main=(i == 0)  # première image = principale
            )
        
        return product

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', None)
        
        # Mettre à jour les champs du produit
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Gérer les nouvelles images si fournies
        if images_data is not None:
            # Supprimer les anciennes images
            instance.images.all().delete()
            
            # Ajouter les nouvelles images
            for i, image_data in enumerate(images_data):
                ProductImage.objects.create(
                    product=instance,
                    image=image_data,
                    is_main=(i == 0)
                )
        
        return instance# products/serializers.py
from rest_framework import serializers
from .models import Category, Product, ProductImage
from django.contrib.auth import get_user_model

User = get_user_model()

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
    farmer = SimpleUserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    
    # Correction: utiliser 'images' pour l'upload au lieu de 'uploaded_images'
    images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )

    class Meta:
        model = Product
        fields = [
            'id', 'farmer', 'category', 'category_id', 'name', 'slug',
            'description', 'price', 'unit', 'stock', 'available',
            'created_at', 'updated_at', 'images', 'images'
        ]
        read_only_fields = ['farmer', 'slug']

    def create(self, validated_data):
        # Extraire les images
        images_data = validated_data.pop('images', [])
        
        # Créer le produit
        product = Product.objects.create(**validated_data)
        
        # Ajouter les images
        for i, image_data in enumerate(images_data):
            ProductImage.objects.create(
                product=product,
                image=image_data,
                is_main=(i == 0)  # première image = principale
            )
        
        return product

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', None)
        
        # Mettre à jour les champs du produit
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Gérer les nouvelles images si fournies
        if images_data is not None:
            # Supprimer les anciennes images
            instance.images.all().delete()
            
            # Ajouter les nouvelles images
            for i, image_data in enumerate(images_data):
                ProductImage.objects.create(
                    product=instance,
                    image=image_data,
                    is_main=(i == 0)
                )
        
        return instance

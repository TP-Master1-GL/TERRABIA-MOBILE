from rest_framework import serializers
from .models import Order, OrderItem, Cart, CartItem, Review
from products.models import Product
from users.serializers import UserSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', read_only=True, max_digits=10, decimal_places=2)
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_name', 'product_price', 'quantity', 'total_price')
    
    def get_total_price(self, obj):
        return obj.quantity * obj.product.price

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ('id', 'user', 'items', 'total_items', 'total_price', 'created_at', 'updated_at')
    
    def get_total_items(self, obj):
        return sum(item.quantity for item in obj.items.all())
    
    def get_total_price(self, obj):
        return sum(item.quantity * item.product.price for item in obj.items.all())

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'quantity', 'unit_price', 'total_price')
    
    def get_total_price(self, obj):
        return obj.total_price

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    buyer_info = UserSerializer(source='buyer', read_only=True)
    farmer_info = UserSerializer(source='farmer', read_only=True)
    delivery_agent_info = UserSerializer(source='delivery_agent', read_only=True)
    
    class Meta:
        model = Order
        fields = ('id', 'buyer', 'buyer_info', 'farmer', 'farmer_info', 
                 'delivery_agent', 'delivery_agent_info', 'status', 
                 'total_amount', 'shipping_address', 'delivery_fee',
                 'items', 'created_at', 'updated_at', 'delivered_at')

class ReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source='reviewer.get_full_name', read_only=True)
    
    class Meta:
        model = Review
        fields = ('id', 'order', 'reviewer', 'reviewer_name', 'reviewed_user', 
                 'rating', 'comment', 'created_at')
        read_only_fields = ('reviewer',)  # AJOUTER CE CHAMP COMME READONLY
    
    def create(self, validated_data):
        # Définir automatiquement le reviewer comme l'utilisateur connecté
        validated_data['reviewer'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate(self, attrs):
        # Vérifier que l'utilisateur peut laisser un avis pour cette commande
        order = attrs.get('order')
        reviewer = self.context['request'].user
        
        if order.buyer != reviewer and order.farmer != reviewer:
            raise serializers.ValidationError("Vous ne pouvez pas laisser d'avis pour cette commande.")
        
        # Vérifier que la commande est livrée
        if order.status != 'delivered':
            raise serializers.ValidationError("Vous ne pouvez laisser un avis que pour les commandes livrées.")
        
        return attrs
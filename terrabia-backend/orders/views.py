from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets, status
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem, Order, ProductRating
from .serializers import CartSerializer, OrderSerializer, RatingSerializer
from .permissions import IsDeliveryAgency
from products.models import Product

# === PANIER ===
@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)

    if request.method == 'GET':
        return Response(CartSerializer(cart).data)

    elif request.method == 'POST':
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        product = get_object_or_404(Product, id=product_id)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()

        return Response(CartSerializer(cart).data)

    elif request.method == 'DELETE':
        product_id = request.data.get('product_id')
        CartItem.objects.filter(cart=cart, product_id=product_id).delete()
        return Response(CartSerializer(cart).data)

# === CHECKOUT ===
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkout(request):
    cart = request.user.cart
    if not cart.items.exists():
        return Response({"error": "Panier vide"}, status=400)

    total = sum(item.product.price * item.quantity for item in cart.items.all())

    order = Order.objects.create(
        buyer=request.user,
        total_amount=total,
        delivery_address=request.data['delivery_address'],
        status='confirmed'
    )
    order.status = 'waiting_delivery'
    order.save()

    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            unit_price=item.product.price
        )
    cart.items.all().delete()
    return Response(OrderSerializer(order).data, status=201)

# === MES COMMANDES ===
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_orders(request):
    orders = Order.objects.filter(buyer=request.user).order_by('-created_at')
    return Response(OrderSerializer(orders, many=True).data)

# === COMMANDES DISPONIBLES POUR LIVRAISON ===
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_orders(request):
    if request.user.user_type != 'delivery_agency':
        return Response({"error": "Accès refusé"}, status=403)

    orders = Order.objects.filter(
        status='waiting_delivery',
        delivery_agency__isnull=True
    )
    return Response(OrderSerializer(orders, many=True).data)

# === ACCEPTER UNE COMMANDE ===
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_order(request, order_id):
    if request.user.user_type != 'delivery_agency':
        return Response({"error": "Seule une agence peut accepter"}, status=403)

    order = get_object_or_404(Order, id=order_id, status='waiting_delivery', delivery_agency__isnull=True)
    order.delivery_agency = request.user
    order.status = 'taken'
    order.save()

    return Response({
        "success": True,
        "message": "Commande prise en charge",
        "order": OrderSerializer(order).data
    })

# === NOTATION PRODUIT ===
class RatingViewSet(viewsets.ModelViewSet):
    queryset = ProductRating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
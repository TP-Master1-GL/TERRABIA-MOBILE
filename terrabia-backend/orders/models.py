from django.db import models
from users.models import User

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('waiting_delivery', 'En attente de livraison'),
        ('taken', 'Prise en charge'),
        ('in_delivery', 'En livraison'),
        ('delivered', 'Livrée'),
        ('cancelled', 'Annulée'),
    )

    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    delivery_agency = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='delivered_orders', limit_choices_to={'user_type': 'delivery_agency'})
    assigned_agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='assigned_deliveries', limit_choices_to={'user_type': 'delivery_agent'})

    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    delivery_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

class ProductRating(models.Model):
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i,i) for i in range(1,6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')
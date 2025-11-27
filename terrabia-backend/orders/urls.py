from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RatingViewSet, cart_view, checkout, my_orders, available_orders, accept_order

router = DefaultRouter()
router.register(r'ratings', RatingViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('cart/', cart_view, name='cart'),
    path('checkout/', checkout, name='checkout'),
    path('my-orders/', my_orders, name='my-orders'),
    path('delivery/available/', available_orders, name='available'),
    path('delivery/accept/<int:order_id>/', accept_order, name='accept'),
]
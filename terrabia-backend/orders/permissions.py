from rest_framework import permissions

class IsBuyer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == 'buyer'

class IsDeliveryAgency(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == 'delivery_agency'
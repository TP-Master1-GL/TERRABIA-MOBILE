from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ('username', 'user_type', 'delivery_agency', 'is_staff')
    list_filter = ('user_type',)
    fieldsets = UserAdmin.fieldsets + (
        ('Informations Terrabia', {
            'fields': ('user_type', 'phone', 'address', 'delivery_agency', 'profile_picture')
        }),
    )
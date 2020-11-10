"""
django-admin configuration for the accounts app.
"""

from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    """
    Admin options for User objects.
    """
    list_display = [
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'is_active',
        'date_joined',
    ]
    ordering = ['email']
    list_filter = ('is_staff', 'is_active')

admin.site.register(User, UserAdmin)

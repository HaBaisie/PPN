from django.contrib import admin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'user_type', 'is_approved')
    actions = ['approve_users']

    def approve_users(self, request, queryset):
        queryset.update(is_approved=True)

from django.contrib import admin
from .models import Policy, Comment, Like, Reshare


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ('name', 'added_by', 'created_at')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('policy', 'user', 'created_at')


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('policy', 'user')


@admin.register(Reshare)
class ReshareAdmin(admin.ModelAdmin):
    list_display = ('policy', 'user')

from django.urls import path
from .views import register, approver_dashboard, approve_user

urlpatterns = [
    path('register/', register, name='register'),
    path('approver/', approver_dashboard, name='approver_dashboard'),
    path('approver/approve/<int:user_id>/', approve_user, name='approve_user'),
]

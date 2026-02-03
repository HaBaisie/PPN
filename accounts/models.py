from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('user', 'Regular User'),
        ('policymaker', 'Policy Maker'),
        ('analyst', 'Analyst'),
        ('approver', 'Approver'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='user')
    certificate = models.FileField(upload_to='certs/', null=True, blank=True)
    is_approved = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Auto-approve regular users and approvers; approvers get staff access
        if self.user_type == 'user':
            self.is_approved = True
        if self.user_type == 'approver':
            self.is_approved = True
            self.is_staff = True
        super().save(*args, **kwargs)

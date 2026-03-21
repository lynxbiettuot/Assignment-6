from django.db import models
from django.contrib.auth.models import User


class CustomerProfile(models.Model):
    """Extended profile for a Customer user (1-1 with Django User)."""
    user          = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    phone         = models.CharField(max_length=20, blank=True, default='')
    address       = models.TextField(blank=True, default='')
    date_of_birth = models.DateField(null=True, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"CustomerProfile({self.user.username})"

from django.db import models

class Shipping(models.Model):
    customer_id = models.IntegerField(null=True, blank=True)
    order_id = models.IntegerField()
    address = models.TextField()
    status = models.CharField(max_length=50, default="Processing")
    created_at = models.DateTimeField(auto_now_add=True)

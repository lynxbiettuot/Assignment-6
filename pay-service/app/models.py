from django.db import models

class Payment(models.Model):
    order_id = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50) # e.g. "Credit Card" or "COD"
    card_number = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=50, default="Success")
    created_at = models.DateTimeField(auto_now_add=True)

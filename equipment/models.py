from django.db import models
from accounts.models import User
from decimal import Decimal
from django.conf import settings

class Equipment(models.Model):
    serial  = models.CharField(max_length=50, unique=True)
    name    = models.CharField(max_length=100)
    brand   = models.CharField(max_length=100)
    price   = models.DecimalField(max_digits=10, decimal_places=2)
    status  = models.BooleanField(default=True)
    added_at= models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveIntegerField(default=0)
    total_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.name} ({self.serial})'


class EquipmentPurchase(models.Model):
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name="purchases"
    )

    quantity = models.PositiveIntegerField()

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    purchase_date = models.DateField()

    purchased_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    def save(self, *args, **kwargs):
        self.total_price = Decimal(self.quantity) * self.unit_price
        super().save(*args, **kwargs)
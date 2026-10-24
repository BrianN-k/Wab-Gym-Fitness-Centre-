from decimal import Decimal
from django.db import models
from packages.models import Package

GENDER_CHOICES = [('male','Male'),('female','Female'),('other','Other')]

class Member(models.Model):
    member_id  = models.CharField(max_length=20, unique=True, blank=True)
    name       = models.CharField(max_length=100)
    dob        = models.DateField()
    nid        = models.CharField(max_length=20, blank=True, null=True)
    gender     = models.CharField(max_length=10, choices=GENDER_CHOICES)
    phone      = models.CharField(max_length=15, unique=True)
    email      = models.EmailField(blank=True, null=True)
    address    = models.TextField(blank=True, null=True)
    referee    = models.CharField(max_length=100, blank=True, null=True)
    package    = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True)
    join_date  = models.DateField()
    expiry_date= models.DateField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_payment= models.DecimalField(max_digits=10, decimal_places=2, default=0)
    photo      = models.ImageField(upload_to='members/', blank=True, null=True)
    status     = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        # Calculate due payment
        if self.package:
            self.due_payment = max(
                Decimal("0.00"),
                Decimal(self.package.fee) - Decimal(self.amount_paid)
            )

        # Save first if this is a new object so it gets a PK
        if self._state.adding:
            super().save(*args, **kwargs)

            if not self.member_id:
                self.member_id = f"MEM{self.pk:04d}"

            # Update only the member_id
            super().save(update_fields=["member_id"])
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.member_id} — {self.name}'

    @property
    def is_expired(self):
        from django.utils import timezone
        return self.expiry_date < timezone.now().date()
    
from django.conf import settings

PAYMENT_METHODS = [
    ("cash", "Cash"),
    ("mpesa", "M-Pesa"),
    ("card", "Card"),
    ("bank", "Bank Transfer"),
]


class MembershipRenewal(models.Model):
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="renewals"
    )

    package = models.ForeignKey(
        Package,
        on_delete=models.SET_NULL,
        null=True
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    balance = models.DecimalField(max_digits=10, decimal_places=2)

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default="cash"
    )

    start_date = models.DateField()
    expiry_date = models.DateField()

    renewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        package = self.package.name if self.package else "No Package"
        return f"{self.member.member_id} - {package} ({self.start_date})"

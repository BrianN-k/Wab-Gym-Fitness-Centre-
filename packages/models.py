from django.db import models

class Package(models.Model):
    name = models.CharField(max_length=50, unique=True)
    duration_days = models.IntegerField()
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name} — KSh {self.fee} ({self.duration_days} days)'

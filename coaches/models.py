from django.db import models
from members.models import Member

class Coach(models.Model):
    coach_id       = models.CharField(max_length=20, unique=True, blank=True)
    name           = models.CharField(max_length=100)
    phone          = models.CharField(max_length=15, unique=True)
    email          = models.EmailField(blank=True, null=True, unique=True)
    specialization = models.CharField(max_length=100, blank=True)
    qualifications = models.TextField(blank=True)
    salary         = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active      = models.BooleanField(default=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.coach_id:
            super().save(*args, **kwargs)
            self.coach_id = f'COA{self.pk:04d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.coach_id} — {self.name}'


class CoachSession(models.Model):
    coach      = models.ForeignKey(Coach, on_delete=models.CASCADE)
    member     = models.ForeignKey(Member, on_delete=models.CASCADE)
    date       = models.DateField()
    amount     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.coach.name} → {self.member.name} on {self.date}'

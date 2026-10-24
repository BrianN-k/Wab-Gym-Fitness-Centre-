from django.db import models
from accounts.models import User
from coaches.models import Coach
from decimal import Decimal

MONTH_CHOICES = [
    ('January','January'),('February','February'),('March','March'),
    ('April','April'),('May','May'),('June','June'),('July','July'),
    ('August','August'),('September','September'),('October','October'),
    ('November','November'),('December','December'),
]

class EmployeeSalary(models.Model):
    employee     = models.ForeignKey(User, on_delete=models.CASCADE)
    month        = models.CharField(max_length=20, choices=MONTH_CHOICES)
    year         = models.IntegerField()
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    allowances   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_salary   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    processed_at = models.DateTimeField(auto_now_add=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL,
                                     null=True, related_name='processed_salaries')

    class Meta:
        unique_together = ['employee','month','year']

    def save(self, *args, **kwargs):
        self.basic_salary = Decimal(self.basic_salary)
        self.allowances = Decimal(self.allowances)
        self.deductions = Decimal(self.deductions)

        self.net_salary = (
            self.basic_salary
            + self.allowances
            - self.deductions
        )

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.employee.get_full_name()} — {self.month} {self.year} — KSh {self.net_salary}'


class CoachSalary(models.Model):
    coach        = models.ForeignKey(Coach, on_delete=models.CASCADE)
    month        = models.CharField(max_length=20, choices=MONTH_CHOICES)
    year         = models.IntegerField()
    amount       = models.DecimalField(max_digits=10, decimal_places=2)
    processed_at = models.DateTimeField(auto_now_add=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ['coach','month','year']

    def __str__(self):
        return f'{self.coach.name} — {self.month} {self.year} — KSh {self.amount}'

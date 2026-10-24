from django.db import models
from members.models import Member
from accounts.models import User
from coaches.models import Coach
from equipment.models import Equipment

DEBIT_REASONS = [
    ('admission', 'Admission'),
    ('package_fee', 'New Membership'),
    ('private_session', 'Private Session'),
    ('renewal', 'Membership Renewal'),
    ('walk_in', 'Walk-in Payment'),
    ('other_income', 'Other Income'),
]

CREDIT_REASONS = [
    ('salary_coach', 'Coach Salary'),
    ('salary_employee', 'Employee Salary'),
    ('buy_equipment', 'Buy Equipment'),
    ('maintenance', 'Maintenance'),
    ('other_expense', 'Other Expense'),
]

MONTH_CHOICES = [
    ('January','January'),('February','February'),('March','March'),
    ('April','April'),('May','May'),('June','June'),('July','July'),
    ('August','August'),('September','September'),('October','October'),
    ('November','November'),('December','December'),
]


class Debit(models.Model):
    """Incoming money - member payments"""
    trx_id      = models.CharField(max_length=20, unique=True, blank=True)
    reason      = models.CharField(max_length=50, choices=DEBIT_REASONS)
    amount      = models.DecimalField(max_digits=10, decimal_places=2)
    date        = models.DateTimeField()
    paid_by     = models.ForeignKey(Member, on_delete=models.CASCADE, null=True, blank=True)
    received_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session = models.ForeignKey("coaches.CoachSession", on_delete=models.SET_NULL, null=True, blank=True)
    

DEBIT_REASONS = [
    ('admission', 'Admission'),
    ('package_fee', 'New Membership'),
    ('private_session', 'Private Session'),
    ('renewal', 'Membership Renewal'),
    ('walk_in', 'Walk-in Payment'),
    ('other_income', 'Other Income'),
]

CREDIT_REASONS = [
    ('salary_coach', 'Coach Salary'),
    ('salary_employee', 'Employee Salary'),
    ('buy_equipment', 'Buy Equipment'),
    ('maintenance', 'Maintenance'),
    ('other_expense', 'Other Expense'),
]

MONTH_CHOICES = [
    ('January','January'),('February','February'),('March','March'),
    ('April','April'),('May','May'),('June','June'),('July','July'),
    ('August','August'),('September','September'),('October','October'),
    ('November','November'),('December','December'),
]


class Debit(models.Model):
    """Incoming money - member payments"""
    trx_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    reason = models.CharField(max_length=50, choices=DEBIT_REASONS)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField()
    paid_by = models.ForeignKey(Member, on_delete=models.CASCADE, null=True, blank=True)
    received_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session = models.ForeignKey(
        "coaches.CoachSession",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        # Force insert only on the first save
        super().save(*args, **kwargs)

        if is_new and not self.trx_id:
            self.trx_id = f"TRX{self.pk:05d}"
            Debit.objects.filter(pk=self.pk).update(trx_id=self.trx_id)

            # Remove force_insert so this becomes an UPDATE
            kwargs.pop("force_insert", None)
            kwargs.pop("force_update", None)

            super().save(update_fields=["trx_id"])

    def __str__(self):
        return f"{self.trx_id} — KSh {self.amount} ({self.reason})"

class Credit(models.Model):
    """Outgoing money - salaries, equipment purchases"""
    trx_id       = models.CharField(max_length=20, unique=True, blank=True)
    reason       = models.CharField(max_length=50, choices=CREDIT_REASONS)
    amount       = models.DecimalField(max_digits=10, decimal_places=2)
    date         = models.DateTimeField()
    is_employee  = models.BooleanField(default=False)
    employee     = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_coach     = models.BooleanField(default=False)
    coach        = models.ForeignKey(Coach, on_delete=models.CASCADE, null=True, blank=True)
    is_equipment = models.BooleanField(default=False)
    equipment    = models.ForeignKey(Equipment, on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
            is_new = self.pk is None
    
            super().save(*args, **kwargs)
    
            if is_new and not self.trx_id:
                self.trx_id = f"TRX{self.pk:05d}"
                super().save(update_fields=["trx_id"])

    def __str__(self):
        return f'{self.trx_id} — KSh {self.amount} ({self.reason})'


class Bill(models.Model):
    """Monthly billing record per member"""
    month          = models.CharField(max_length=20, choices=MONTH_CHOICES)
    year           = models.IntegerField()
    reason         = models.CharField(max_length=50, choices=DEBIT_REASONS, default='package_fee')
    total_amount   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_amount    = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_amount     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    advanced_amount= models.DecimalField(max_digits=10, decimal_places=2, default=0)
    member         = models.ForeignKey(Member, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.month} {self.year} — {self.member.name}'


    def __str__(self):
        return f'{self.trx_id} — KSh {self.amount} ({self.reason})'


class Credit(models.Model):
    """Outgoing money — salaries, equipment purchases"""
    trx_id       = models.CharField(max_length=20, unique=True, blank=True)
    reason       = models.CharField(max_length=50, choices=CREDIT_REASONS)
    amount       = models.DecimalField(max_digits=10, decimal_places=2)
    date         = models.DateTimeField()
    is_employee  = models.BooleanField(default=False)
    employee     = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_coach     = models.BooleanField(default=False)
    coach        = models.ForeignKey(Coach, on_delete=models.CASCADE, null=True, blank=True)
    is_equipment = models.BooleanField(default=False)
    equipment    = models.ForeignKey(Equipment, on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
            is_new = self.pk is None
    
            super().save(*args, **kwargs)
    
            if is_new and not self.trx_id:
                self.trx_id = f"TRX{self.pk:05d}"
                super().save(update_fields=["trx_id"])

    def __str__(self):
        return f'{self.trx_id} — KSh {self.amount} ({self.reason})'


class Bill(models.Model):
    """Monthly billing record per member"""
    month          = models.CharField(max_length=20, choices=MONTH_CHOICES)
    year           = models.IntegerField()
    reason         = models.CharField(max_length=50, choices=DEBIT_REASONS, default='package_fee')
    total_amount   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_amount    = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_amount     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    advanced_amount= models.DecimalField(max_digits=10, decimal_places=2, default=0)
    member         = models.ForeignKey(Member, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.month} {self.year} — {self.member.name}'

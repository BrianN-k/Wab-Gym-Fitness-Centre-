from django.db import models
from accounts.models import User

class Attendance(models.Model):
    TYPE_CHOICES = [('employee','Employee'),('coach','Coach')]
    employee    = models.ForeignKey(User, on_delete=models.CASCADE)
    date        = models.DateField()
    time_in     = models.TimeField()
    time_out    = models.TimeField(null=True, blank=True)
    att_type    = models.CharField(max_length=10, choices=TYPE_CHOICES, default='employee')

    class Meta:
        unique_together = ['employee','date']

    def __str__(self):
        return f'{self.employee.get_full_name()} — {self.date}'

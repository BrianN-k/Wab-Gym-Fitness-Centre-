# attendance/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Attendance
from accounts.models import User


@login_required
def attendance_list(request):
    today = timezone.now().date()
    date_filter = request.GET.get('date', str(today))
    records = Attendance.objects.filter(date=date_filter).select_related('employee').order_by('time_in')
    employees = User.objects.filter(is_active=True)
    return render(request, 'attendance/attendance_list.html', {
        'records': records, 'employees': employees,
        'date_filter': date_filter, 'today': today
    })


@login_required
def attendance_record(request):
    if request.method == 'POST':
        employee_id = request.POST.get('employee')
        date        = request.POST.get('date')
        time_in     = request.POST.get('time_in')

        if not employee_id:
            messages.error(request, 'Please select an employee.')
            return redirect('attendance_list')

        employee = get_object_or_404(User, pk=employee_id)
        if Attendance.objects.filter(employee=employee, date=date).exists():
            messages.warning(request, f'{employee.get_full_name()} already has attendance recorded for {date}.')
            return redirect('attendance_list')

        Attendance.objects.create(employee=employee, date=date, time_in=time_in)
        messages.success(request, f'Attendance recorded for {employee.get_full_name()} on {date}.')
    return redirect('attendance_list')

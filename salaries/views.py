from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import EmployeeSalary, CoachSalary
from accounts.models import User
from coaches.models import Coach
from django.http import HttpResponseForbidden
from decimal import Decimal
from payments.models import Credit

def salary_permission(request):
    if request.user.role not in ["admin", "accountant"]:
        return HttpResponseForbidden(
            "You do not have permission to access the Salary module."
        )
    return None

@login_required
def salary_list(request):

    permission = salary_permission(request)
    if permission:
        return permission

    emp_salaries = EmployeeSalary.objects.select_related(
        'employee', 'processed_by'
    ).order_by('-year', '-id')

    coach_salaries = CoachSalary.objects.select_related(
        'coach', 'processed_by'
    ).order_by('-year', '-id')

    employees = User.objects.filter(is_active=True)
    coaches = Coach.objects.filter(is_active=True)

    return render(request, 'salaries/salary_list.html', {
        'emp_salaries': emp_salaries,
        'coach_salaries': coach_salaries,
        'employees': employees,
        'coaches': coaches,
        'year': timezone.now().year,
    })

@login_required
def process_employee_salary(request):

    permission = salary_permission(request)
    if permission:
        return permission
    
    if request.method == 'POST':
        emp_id       = request.POST.get('employee')
        month        = request.POST.get('month')
        year         = request.POST.get('year', timezone.now().year)
        basic_salary = Decimal(request.POST.get('basic_salary') or "0")
        allowances = Decimal(request.POST.get('allowances') or "0")
        deductions = Decimal(request.POST.get('deductions') or "0")

        errors = []
        if not emp_id:
            errors.append('Please select an employee.')
        if not month:
            errors.append('Please select a month.')
        if float(basic_salary) < 0:
            errors.append('Salary values cannot be negative.')
        if float(deductions) > float(basic_salary) + float(allowances):
            errors.append('Deductions cannot exceed total salary.')

        if errors:
            for e in errors:
                messages.error(request, e)
            return redirect('salary_list')

        employee = get_object_or_404(User, pk=emp_id)

        if EmployeeSalary.objects.filter(employee=employee, month=month, year=year).exists():
            messages.error(request, f'Salary already processed for {employee.get_full_name()} in {month} {year}.')
            return redirect('salary_list')

        sal = EmployeeSalary(
            employee=employee, month=month, year=int(year),
            basic_salary=basic_salary, allowances=allowances,
            deductions=deductions, processed_by=request.user
        )
        sal.save()
        Credit.objects.create(
            reason="salary_employee",
            amount=sal.net_salary,
            date=timezone.now(),
            employee=employee,
            is_employee=True,
        )
        messages.success(request, f'Salary of KSh {sal.net_salary} processed for {employee.get_full_name()}.')
    return redirect('salary_list')


@login_required
def process_coach_salary(request):
    if request.method == 'POST':
        coach_id = request.POST.get('coach')
        month    = request.POST.get('month')
        year     = request.POST.get('year', timezone.now().year)
        amount   = request.POST.get('amount', 0)

        if not coach_id or not month:
            messages.error(request, 'Please fill all fields.')
            return redirect('salary_list')

        coach = get_object_or_404(Coach, pk=coach_id)

        if CoachSalary.objects.filter(coach=coach, month=month, year=year).exists():
            messages.error(request, f'Salary already processed for {coach.name} in {month} {year}.')
            return redirect('salary_list')

        salary = CoachSalary.objects.create(
            coach=coach,
            month=month,
            year=int(year),
            amount=amount,
            processed_by=request.user
        )

        Credit.objects.create(
            reason="salary_coach",
            amount=Decimal(amount),
            date=timezone.now(),
            coach=coach,
            is_coach=True,
        )

        messages.success(
            request,
            f'Coach salary of KSh {salary.amount} processed for {coach.name}.'
        )
    return redirect('salary_list')

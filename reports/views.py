from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils import timezone
from members.models import Member
from payments.models import Debit, Credit, Bill
from attendance.models import Attendance
from salaries.models import EmployeeSalary, CoachSalary
from coaches.models import Coach
from accounts.models import User
import json

@login_required
def dashboard(request):
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year

    # Stats
    total_members = Member.objects.filter(status=True).count()
    expired_members = Member.objects.filter(status=True, expiry_date__lt=today).count()
    expiring_soon = Member.objects.filter(
        status=True,
        expiry_date__gte=today,
        expiry_date__lte=today + timezone.timedelta(days=7)
    ).order_by('expiry_date')

    total_coaches = Coach.objects.filter(is_active=True).count()
    total_staff = User.objects.filter(is_active=True).count()

    # Monthly income
    monthly_income = Debit.objects.filter(
        date__month=current_month, date__year=current_year
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Monthly expenses
    monthly_expense = Credit.objects.filter(
        date__month=current_month, date__year=current_year
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Pending salary
    pending_coach_salary = Coach.objects.filter(is_active=True).aggregate(
        total=Sum('salary'))['total'] or 0
    pending_emp_salary = User.objects.filter(is_active=True).count() * 0

    # New members this month
    new_members = Member.objects.filter(
        join_date__month=current_month,
        join_date__year=current_year
    ).count()

    # Today's attendance
    today_attendance = Attendance.objects.filter(date=today).count()

    # Monthly income chart (last 6 months)
    months_labels = []
    months_income = []
    months_expense = []
    for i in range(5, -1, -1):
        from datetime import date
        import calendar
        d = today.replace(day=1)
        month_num = (d.month - i - 1) % 12 + 1
        year_num = d.year - ((d.month - i - 1) // 12)
        label = date(year_num, month_num, 1).strftime('%b %Y')
        inc = Debit.objects.filter(
            date__month=month_num, date__year=year_num
        ).aggregate(t=Sum('amount'))['t'] or 0
        exp = Credit.objects.filter(
            date__month=month_num, date__year=year_num
        ).aggregate(t=Sum('amount'))['t'] or 0
        months_labels.append(label)
        months_income.append(float(inc))
        months_expense.append(float(exp))

    # Recent transactions
    recent_debits = Debit.objects.select_related('paid_by').order_by('-date')[:5]
    recent_credits = Credit.objects.order_by('-date')[:5]

    context = {
        'total_members': total_members,
        'expired_members': expired_members,
        'expiring_soon': expiring_soon,
        'total_coaches': total_coaches,
        'total_staff': total_staff,
        'monthly_income': monthly_income,
        'monthly_expense': monthly_expense,
        'new_members': new_members,
        'today_attendance': today_attendance,
        'months_labels': json.dumps(months_labels),
        'months_income': json.dumps(months_income),
        'months_expense': json.dumps(months_expense),
        'recent_debits': recent_debits,
        'recent_credits': recent_credits,
        'pending_coach_salary': pending_coach_salary,
        'today': today,
    }
    return render(request, 'reports/dashboard.html', context)


@login_required
def reports_page(request):
    from datetime import date
    report_type = request.GET.get('type', 'members')
    date_from = request.GET.get('from', '')
    date_to = request.GET.get('to', '')

    data = []
    title = ''

    if report_type == 'members':
        title = 'Member Registration Report'
        qs = Member.objects.all().order_by('-join_date')
        if date_from:
            qs = qs.filter(join_date__gte=date_from)
        if date_to:
            qs = qs.filter(join_date__lte=date_to)
        data = qs

    elif report_type == 'payments':
        title = 'Payment Collection Report'
        qs = Debit.objects.select_related('paid_by','received_by').order_by('-date')
        if date_from:
            qs = qs.filter(date__date__gte=date_from)
        if date_to:
            qs = qs.filter(date__date__lte=date_to)
        data = qs

    elif report_type == 'attendance':
        title = 'Attendance Report'
        qs = Attendance.objects.select_related('employee').order_by('-date')
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        data = qs

    elif report_type == 'payroll':
        title = 'Payroll Report'
        qs = EmployeeSalary.objects.select_related('employee').order_by('-year','-id')
        data = qs

    elif report_type == 'expiry':
        title = 'Subscription Expiry Report'
        days = int(request.GET.get('days', 7))
        qs = Member.objects.filter(
            status=True,
            expiry_date__lte=date.today() + timezone.timedelta(days=days)
        ).order_by('expiry_date')
        data = qs

    context = {
        'report_type': report_type,
        'title': title,
        'data': data,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'reports/reports.html', context)

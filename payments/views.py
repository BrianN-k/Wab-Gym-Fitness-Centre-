from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Debit, Credit, Bill
from members.models import Member
from coaches.models import Coach
from equipment.models import Equipment
from accounts.models import User


@login_required
def payment_list(request):
    debits = Debit.objects.select_related('paid_by','received_by').order_by('-date')
    credits = Credit.objects.order_by('-date')
    employees = User.objects.filter(is_active=True)
    coaches = Coach.objects.filter(is_active=True)

    # Search
    emp_q = request.GET.get('emp_q','')
    coach_q = request.GET.get('coach_q','')
    if emp_q:
        employees = employees.filter(first_name__icontains=emp_q) | \
                    employees.filter(last_name__icontains=emp_q)
    if coach_q:
        coaches = coaches.filter(name__icontains=coach_q)

    return render(request, 'payments/payment_list.html', {
        'debits': debits, 'credits': credits,
        'employees': employees, 'coaches': coaches,
        'emp_q': emp_q, 'coach_q': coach_q,
    })


@login_required
def debit_create(request):
    """Record incoming payment from member"""
    members = Member.objects.filter(status=True)
    if request.method == 'POST':
        member_id = request.POST.get('member')
        reason    = request.POST.get('reason')
        amount    = request.POST.get('amount')
        date_str  = request.POST.get('date')

        errors = []
        if not member_id:
            errors.append('Please select a member.')
        if not amount or float(amount) <= 0:
            errors.append('Amount must be greater than zero.')
        if errors:
            for e in errors:
                messages.error(request, e)
            return redirect('payment_list')

        member = get_object_or_404(Member, pk=member_id)
        from datetime import datetime
        dt = datetime.fromisoformat(date_str) if date_str else timezone.now()

        debit = Debit(
            reason=reason,
            amount=amount,
            date=dt,
            paid_by=member,
            received_by=request.user
        )
        debit.save()

        # Update member due payment
        member.due_payment = max(0, float(member.due_payment) - float(amount))
        member.save()

        # Create/update bill
        month_name = dt.strftime('%B')
        bill, _ = Bill.objects.get_or_create(
            member=member, month=month_name, year=dt.year,
            defaults={'reason': reason, 'total_amount': member.package.fee if member.package else 0}
        )
        bill.paid_amount = float(bill.paid_amount) + float(amount)
        bill.due_amount = max(0, float(bill.total_amount) - float(bill.paid_amount))
        bill.save()

        messages.success(request, f'Payment of KSh {amount} recorded for {member.name}. TRX: {debit.trx_id}')
        return redirect('payment_list')

    return render(request, 'payments/debit_form.html', {'members': members})


@login_required
def credit_create(request):
    """Record outgoing payment — salary or equipment"""
    employees = User.objects.filter(is_active=True)
    coaches = Coach.objects.filter(is_active=True)
    equipments = Equipment.objects.all()

    if request.method == 'POST':
        reason = request.POST.get('reason')
        amount = request.POST.get('amount')
        date_str = request.POST.get('date')
        from datetime import datetime
        dt = datetime.fromisoformat(date_str) if date_str else timezone.now()

        credit = Credit(reason=reason, amount=amount, date=dt)

        if reason == 'salary_employee':
            emp_id = request.POST.get('employee')
            if emp_id:
                credit.is_employee = True
                credit.employee = get_object_or_404(User, pk=emp_id)
        elif reason == 'salary_coach':
            coach_id = request.POST.get('coach')
            if coach_id:
                credit.is_coach = True
                credit.coach = get_object_or_404(Coach, pk=coach_id)
        elif reason == 'buy_equipment':
            eq_id = request.POST.get('equipment')
            if eq_id:
                credit.is_equipment = True
                credit.equipment = get_object_or_404(Equipment, pk=eq_id)

        credit.save()
        messages.success(request, f'Credit transaction of KSh {amount} recorded. TRX: {credit.trx_id}')
        return redirect('payment_list')

    return render(request, 'payments/credit_form.html', {
        'employees': employees, 'coaches': coaches, 'equipments': equipments
    })

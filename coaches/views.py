from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Coach, CoachSession
from members.models import Member
from payments.models import Debit
from decimal import Decimal
from django.utils import timezone

@login_required
def coach_list(request):
    q = request.GET.get('q', '')
    coaches = Coach.objects.all().order_by('name')
    if q:
        coaches = coaches.filter(name__icontains=q)
    return render(request, 'coaches/coach_list.html', {'coaches': coaches, 'q': q})


@login_required
def coach_create(request):
    if request.method == 'POST':
        name           = request.POST.get('name', '').strip()
        phone          = request.POST.get('phone', '').strip()
        email          = request.POST.get('email', '').strip() or None
        specialization = request.POST.get('specialization', '')
        qualifications = request.POST.get('qualifications', '')
        salary         = request.POST.get('salary', 0)

        errors = []
        if not name:
            errors.append('Coach name is required.')
        if not phone:
            errors.append('Phone number is required.')
        elif Coach.objects.filter(phone=phone).exists():
            errors.append('A coach with this phone already exists.')
        if email and Coach.objects.filter(email=email).exists():
            errors.append('A coach with this email already exists.')

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'coaches/coach_form.html',
                          {'title': 'Register Coach', 'post': request.POST})

        coach = Coach(name=name, phone=phone, email=email,
                      specialization=specialization,
                      qualifications=qualifications, salary=salary)
        coach.save()
        messages.success(request, f'Coach {name} registered. ID: {coach.coach_id}')
        return redirect('coach_list')

    return render(request, 'coaches/coach_form.html', {'title': 'Register Coach'})


@login_required
def coach_detail(request, pk):
    coach = get_object_or_404(Coach, pk=pk)
    sessions = CoachSession.objects.filter(coach=coach).select_related('member').order_by('-date')
    members = Member.objects.filter(status=True)
    return render(request, 'coaches/coach_detail.html', {
        'coach': coach, 'sessions': sessions, 'members': members
    })


@login_required
def coach_edit(request, pk):
    coach = get_object_or_404(Coach, pk=pk)
    if request.method == 'POST':
        coach.name           = request.POST.get('name', coach.name)
        coach.phone          = request.POST.get('phone', coach.phone)
        coach.email          = request.POST.get('email', '') or None
        coach.specialization = request.POST.get('specialization', coach.specialization)
        coach.qualifications = request.POST.get('qualifications', coach.qualifications)
        coach.salary         = request.POST.get('salary', coach.salary)
        coach.save()
        messages.success(request, 'Coach updated successfully.')
        return redirect('coach_detail', pk=pk)
    return render(request, 'coaches/coach_form.html',
                  {'title': 'Edit Coach', 'coach': coach})


@login_required
def book_session(request, pk):
    coach = get_object_or_404(Coach, pk=pk)
    if request.method == 'POST':
        member_id = request.POST.get('member')
        date      = request.POST.get('date')
        amount    = request.POST.get('amount', 0)
        member = get_object_or_404(Member, pk=member_id)
        session = CoachSession.objects.create(
            coach=coach,
            member=member,
            date=date,
            amount=amount
        )

        # Automatically record the payment
        Debit.objects.create(
            reason="private_session",
            amount=Decimal(amount),
            date=timezone.now(),
            paid_by=member,
            received_by=request.user,
        )

        messages.success(
            request,
            f'Session booked for {member.name} with {coach.name}.'
        )
                
    return redirect('coach_detail', pk=pk)


@login_required
def coach_toggle(request, pk):
    coach = get_object_or_404(Coach, pk=pk)
    coach.is_active = not coach.is_active
    coach.save()
    messages.success(request, f'Coach {coach.name} {"activated" if coach.is_active else "deactivated"}.')
    return redirect('coach_list')

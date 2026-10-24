from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Member
from packages.models import Package
from payments.models import Bill, Debit
from datetime import timedelta
from datetime import date
from decimal import Decimal
from .models import Member, MembershipRenewal
from payments.models import Debit

@login_required
def member_list(request):
    q = request.GET.get('q', '')
    members = Member.objects.select_related('package').order_by('-created_at')
    if q:
        members = members.filter(name__icontains=q) | \
                  members.filter(phone__icontains=q) | \
                  members.filter(member_id__icontains=q)
    members = members.distinct()
    return render(request, 'members/member_list.html', {
        'members': members, 'q': q,
        'today': timezone.now().date()
    })


@login_required
def member_create(request):
    packages = Package.objects.filter(is_active=True)
    if request.method == 'POST':
        name        = request.POST.get('name', '').strip()
        dob         = request.POST.get('dob')
        nid         = request.POST.get('nid', '')
        gender      = request.POST.get('gender')
        phone       = request.POST.get('phone', '').strip()
        email       = request.POST.get('email', '').strip() or None
        address     = request.POST.get('address', '')
        referee     = request.POST.get('referee', '')
        package_id  = request.POST.get('package')
        join_date   = request.POST.get('join_date')
        photo       = request.FILES.get('photo')
        amount_paid = request.POST.get('amount_paid', 0) or 0

        # Validation
        errors = []
        if not name:
            errors.append('Full name is required.')
        if not phone:
            errors.append('Phone number is required.')
        elif Member.objects.filter(phone=phone).exists():
            errors.append('A member with this phone number already exists.')
        if email and Member.objects.filter(email=email).exists():
            errors.append('A member with this email already exists.')
        if not package_id:
            errors.append('Please select a membership package.')
        if not join_date:
            errors.append('Join date is required.')

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'members/member_form.html', {
                'packages': packages, 'post': request.POST, 'title': 'Register New Member'
            })

        pkg = get_object_or_404(Package, pk=package_id)
        from datetime import date
        jd = date.fromisoformat(join_date)
        expiry = jd + timedelta(days=pkg.duration_days)

        member = Member(
            name=name, dob=dob, nid=nid, gender=gender,
            phone=phone, email=email, address=address,
            referee=referee, package=pkg,
            join_date=jd, expiry_date=expiry,
            amount_paid=amount_paid,
        )
        if photo:
            member.photo = photo
        member.save()
        Debit.objects.create(
            reason="package_fee",
            amount=member.amount_paid,
            date=timezone.now(),
            paid_by=member,
            received_by=request.user,
        )
        messages.success(request, f'Member {name} registered successfully. ID: {member.member_id}')
        return redirect('member_detail', pk=member.pk)

    return render(request, 'members/member_form.html', {
        'packages': packages, 'title': 'Register New Member'
    })


@login_required
def member_detail(request, pk):
    member = get_object_or_404(Member, pk=pk)
    bills = Bill.objects.filter(member=member).order_by('-year', '-id')
    debits = Debit.objects.filter(paid_by=member).order_by('-date')
    today = timezone.now().date()
    return render(request, 'members/member_detail.html', {
        'member': member, 'bills': bills,
        'debits': debits, 'today': today
    })


@login_required
def member_edit(request, pk):
    member = get_object_or_404(Member, pk=pk)
    packages = Package.objects.filter(is_active=True)
    if request.method == 'POST':
        member.name    = request.POST.get('name', member.name)
        member.dob     = request.POST.get('dob', member.dob)
        member.nid     = request.POST.get('nid', member.nid)
        member.gender  = request.POST.get('gender', member.gender)
        phone = request.POST.get('phone', '').strip()
        if phone and phone != member.phone:
            if Member.objects.filter(phone=phone).exclude(pk=pk).exists():
                messages.error(request, 'Phone already used by another member.')
                return render(request, 'members/member_form.html',
                              {'packages': packages, 'member': member, 'title': 'Edit Member'})
            member.phone = phone

            email = request.POST.get("email", "").strip()

            if email and email != member.email:
                if Member.objects.filter(email=email).exclude(pk=pk).exists():
                    messages.error(request, "Email already exists.")
                    return render(
                        request,
                        "members/member_form.html",
                        {
                            "packages": packages,
                            "member": member,
                            "title": "Edit Member",
                        },
                    )

            member.email = email

            join_date = request.POST.get("join_date")

            if join_date:
                member.join_date = join_date

        member.address = request.POST.get('address', member.address)
        member.referee = request.POST.get('referee', member.referee)
        member.amount_paid = request.POST.get('amount_paid', member.amount_paid)
        if request.FILES.get('photo'):
            member.photo = request.FILES['photo']
        pkg_id = request.POST.get('package')
        if pkg_id:
            pkg = get_object_or_404(Package, pk=pkg_id)
            member.package = pkg

            join_date = request.POST.get("join_date")

            if join_date:
                jd = date.fromisoformat(join_date)
                member.join_date = jd
                member.expiry_date = jd + timedelta(days=pkg.duration_days)
            member.save()
            messages.success(request, 'Member updated successfully.')
        return redirect('member_detail', pk=pk)

    return render(request, 'members/member_form.html', {
        'packages': packages, 'member': member, 'title': 'Edit Member'
    })


@login_required
def member_toggle(request, pk):
    member = get_object_or_404(Member, pk=pk)
    member.status = not member.status
    member.save()
    status = 'activated' if member.status else 'deactivated'
    messages.success(request, f'Member {member.name} {status}.')
    return redirect('member_detail', pk=pk)

@login_required
def member_renew(request, pk):

    member = get_object_or_404(Member, pk=pk)
    packages = Package.objects.filter(is_active=True)

    if request.method == "POST":

        package = get_object_or_404(
            Package,
            pk=request.POST["package"]
        )

        amount_paid = Decimal(request.POST.get("amount_paid") or "0")

        balance = max(
            Decimal("0.00"),
            Decimal(package.fee) - amount_paid
        )

        # If membership is still active, extend from expiry date.
        # Otherwise start today.
        if member.expiry_date >= timezone.now().date():
            start_date = member.expiry_date
        else:
            start_date = timezone.now().date()

        expiry_date = start_date + timedelta(
            days=package.duration_days
        )

        # Update member
        member.package = package
        member.amount_paid = amount_paid
        member.due_payment = balance
        member.expiry_date = expiry_date
        member.status = True
        member.save()

        Debit.objects.create(
            reason="renewal",
            amount=amount_paid,
            date=timezone.now(),
            paid_by=member,
            received_by=request.user,
        )

        # Save renewal history
        MembershipRenewal.objects.create(
            member=member,
            package=package,
            amount=package.fee,
            amount_paid=amount_paid,
            balance=balance,
            payment_method=request.POST.get(
                "payment_method",
                "cash"
            ),
            start_date=start_date,
            expiry_date=expiry_date,
            renewed_by=request.user
        )

        messages.success(
            request,
            f"{member.name}'s membership has been renewed successfully."
        )

        return redirect("member_detail", pk=member.pk)

    return render(
        request,
        "members/renew_member.html",
        {
            "member": member,
            "packages": packages,
        }
    )
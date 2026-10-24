from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Package


@login_required
def package_list(request):
    packages = Package.objects.all().order_by('fee')
    return render(request, 'packages/package_list.html', {'packages': packages})


@login_required
def package_create(request):
    if request.method == 'POST':
        name          = request.POST.get('name', '').strip()
        duration_days = request.POST.get('duration_days', 0)
        fee           = request.POST.get('fee', 0)
        description   = request.POST.get('description', '')

        errors = []
        if not name:
            errors.append('Package name is required.')
        elif Package.objects.filter(name__iexact=name).exists():
            errors.append('A package with this name already exists.')
        if float(fee) <= 0:
            errors.append('Fee must be greater than zero.')
        if int(duration_days) <= 0:
            errors.append('Duration must be greater than zero days.')

        if errors:
            for e in errors:
                messages.error(request, e)
            return redirect('package_list')

        Package.objects.create(
            name=name, duration_days=duration_days,
            fee=fee, description=description
        )
        messages.success(request, f'Package "{name}" created successfully.')
        return redirect('package_list')

    return redirect('package_list')


@login_required
def package_edit(request, pk):
    pkg = get_object_or_404(Package, pk=pk)
    if request.method == 'POST':
        pkg.name          = request.POST.get('name', pkg.name)
        pkg.duration_days = request.POST.get('duration_days', pkg.duration_days)
        pkg.fee           = request.POST.get('fee', pkg.fee)
        pkg.description   = request.POST.get('description', pkg.description)
        pkg.save()
        messages.success(request, f'Package "{pkg.name}" updated.')
        return redirect('package_list')
    return render(request, 'packages/package_form.html', {'pkg': pkg})


@login_required
def package_toggle(request, pk):
    pkg = get_object_or_404(Package, pk=pk)
    from members.models import Member
    if pkg.is_active and Member.objects.filter(package=pkg).exists():
        messages.error(request, f'Cannot deactivate "{pkg.name}" — members are assigned to it.')
        return redirect('package_list')
    pkg.is_active = not pkg.is_active
    pkg.save()
    messages.success(request, f'Package "{pkg.name}" {"activated" if pkg.is_active else "deactivated"}.')
    return redirect('package_list')

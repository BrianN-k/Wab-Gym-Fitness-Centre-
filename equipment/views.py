from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Equipment, EquipmentPurchase
from payments.models import Credit
from django.utils import timezone
from decimal import Decimal

@login_required
def equipment_list(request):
    equipment = Equipment.objects.all().order_by('-added_at')
    return render(request, 'equipment/equipment_list.html', {'equipment': equipment})


@login_required
def equipment_create(request):
    if request.method == 'POST':
        serial = request.POST.get('serial', '').strip()
        name   = request.POST.get('name', '').strip()
        brand  = request.POST.get('brand', '').strip()
        price  = request.POST.get('price', 0)
        quantity = int(request.POST.get("quantity", 1))

        errors = []
        if not serial:
            errors.append('Serial number is required.')
        elif Equipment.objects.filter(serial=serial).exists():
            errors.append('Equipment with this serial already exists.')
        if not name:
            errors.append('Equipment name is required.')

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'equipment/equipment_form.html', {'post': request.POST})

        equipment = Equipment.objects.create(serial=serial, name=name, brand=brand, price=Decimal(price), quantity=quantity, total_value=Decimal(price) * quantity,)
        EquipmentPurchase.objects.create(
            equipment=equipment,
            quantity=quantity,
            unit_price=Decimal(price),
            purchase_date=timezone.now().date(),
            purchased_by=request.user,
        )
        Credit.objects.create(
            reason="buy_equipment",
            amount=Decimal(price) * quantity,
            date=timezone.now(),
            equipment=equipment,
            is_equipment=True,
        )
        messages.success(request, f'Equipment "{name}" added successfully.')
        return redirect('equipment_list')

    return render(request, 'equipment/equipment_form.html', {})

@login_required
def add_purchase(request, pk):
    equipment = get_object_or_404(Equipment, pk=pk)

    if request.method == "POST":

        quantity = int(request.POST["quantity"])
        unit_price = equipment.price
        purchase_date = request.POST["purchase_date"]

        purchase = EquipmentPurchase.objects.create(
            equipment=equipment,
            quantity=quantity,
            unit_price=unit_price,
            purchase_date=purchase_date,
            purchased_by=request.user,
        )

        # Update inventory
        equipment.quantity += quantity
        equipment.total_value += purchase.total_price
        equipment.save()

        # Record expense transaction
        Credit.objects.create(
            reason="buy_equipment",
            amount=purchase.total_price,
            date=timezone.now(),
            equipment=equipment,
            is_equipment=True,
        )

        messages.success(request, "Equipment stock updated successfully.")
        return redirect("equipment_list")

    return render(request, "equipment/add_purchase.html", {
        "equipment": equipment
    })

@login_required
def equipment_toggle(request, pk):
    eq = get_object_or_404(Equipment, pk=pk)
    eq.status = not eq.status
    eq.save()
    messages.success(request, f'Equipment "{eq.name}" status updated.')
    return redirect('equipment_list')

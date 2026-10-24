"""
WAB Gym Management System — Setup Script
Run this ONCE after migrations to create admin user and sample data.

Usage:
    python manage.py shell < setup_data.py
    OR
    python manage.py runscript setup_data   (if django-extensions installed)
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wabgym.settings')

from accounts.models import User
from packages.models import Package
from members.models import Member
from coaches.models import Coach
from equipment.models import Equipment
from datetime import date, timedelta

print("=" * 50)
print("WAB GYM MANAGEMENT SYSTEM — SETUP")
print("=" * 50)

# ── 1. CREATE USERS ───────────────────────────────
print("\n[1] Creating users...")

if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser(
        username='admin',
        password='Admin@123',
        first_name='System',
        last_name='Admin',
        email='admin@wabgym.co.ke',
        role='admin'
    )
    print(f"  ✓ Admin user created: admin / Admin@123")

if not User.objects.filter(username='manager').exists():
    User.objects.create_user(
        username='manager',
        password='Manager@123',
        first_name='Gym',
        last_name='Manager',
        email='manager@wabgym.co.ke',
        role='manager'
    )
    print(f"  ✓ Manager created: manager / Manager@123")

if not User.objects.filter(username='reception').exists():
    User.objects.create_user(
        username='reception',
        password='Recep@123',
        first_name='Sarah',
        last_name='Njoroge',
        email='reception@wabgym.co.ke',
        role='employee'
    )
    print(f"  ✓ Receptionist created: reception / Recep@123")

if not User.objects.filter(username='accountant').exists():
    User.objects.create_user(
        username='accountant',
        password='Acct@123',
        first_name='Tom',
        last_name='Ochieng',
        email='accountant@wabgym.co.ke',
        role='employee'
    )
    print(f"  ✓ Accountant created: accountant / Acct@123")

# ── 2. CREATE PACKAGES ────────────────────────────
print("\n[2] Creating membership packages...")

packages_data = [
    {'name': 'Daily',     'duration_days': 1,   'fee': 300,   'description': 'Single day access'},
    {'name': 'Weekly',    'duration_days': 7,   'fee': 1500,  'description': 'One week access'},
    {'name': 'Monthly',   'duration_days': 30,  'fee': 3000,  'description': 'One month access — most popular'},
    {'name': 'Quarterly', 'duration_days': 90,  'fee': 8000,  'description': 'Three months access'},
    {'name': 'Annual',    'duration_days': 365, 'fee': 25000, 'description': 'Full year access — best value'},
]

for pd in packages_data:
    pkg, created = Package.objects.get_or_create(name=pd['name'], defaults=pd)
    if created:
        print(f"  ✓ Package: {pkg.name} — KSh {pkg.fee} ({pkg.duration_days} days)")

# ── 3. CREATE COACHES ─────────────────────────────
print("\n[3] Creating coaches...")

coaches_data = [
    {'name': 'James Mwangi',   'phone': '0711000001', 'email': 'james@wabgym.co.ke',
     'specialization': 'Bodybuilding', 'salary': 35000},
    {'name': 'Grace Adhiambo', 'phone': '0711000002', 'email': 'grace@wabgym.co.ke',
     'specialization': 'Weight Management', 'salary': 35000},
    {'name': 'Peter Kamau',    'phone': '0711000003', 'email': 'peter@wabgym.co.ke',
     'specialization': 'Personal Training', 'salary': 40000},
]

for cd in coaches_data:
    coach, created = Coach.objects.get_or_create(phone=cd['phone'], defaults=cd)
    if created:
        print(f"  ✓ Coach: {coach.name} ({coach.specialization})")

# ── 4. CREATE SAMPLE MEMBERS ─────────────────────
print("\n[4] Creating sample members...")

monthly_pkg = Package.objects.get(name='Monthly')
quarterly_pkg = Package.objects.get(name='Quarterly')
annual_pkg = Package.objects.get(name='Annual')

today = date.today()

members_data = [
    {'name': 'Alice Njeri',    'phone': '0712345678', 'dob': date(1995, 3, 15),
     'gender': 'female', 'package': monthly_pkg,   'join_date': today - timedelta(days=10)},
    {'name': 'Brian Otieno',   'phone': '0723456789', 'dob': date(1990, 7, 22),
     'gender': 'male',   'package': quarterly_pkg, 'join_date': today - timedelta(days=45)},
    {'name': 'Carol Wambui',   'phone': '0734567890', 'dob': date(1998, 11, 5),
     'gender': 'female', 'package': annual_pkg,    'join_date': today - timedelta(days=90)},
    {'name': 'David Kipchoge', 'phone': '0745678901', 'dob': date(1985, 4, 18),
     'gender': 'male',   'package': monthly_pkg,   'join_date': today - timedelta(days=5)},
    {'name': 'Evelyn Achieng', 'phone': '0756789012', 'dob': date(2000, 9, 30),
     'gender': 'female', 'package': quarterly_pkg, 'join_date': today - timedelta(days=20)},
]

for md in members_data:
    if not Member.objects.filter(phone=md['phone']).exists():
        pkg = md.pop('package')
        jd = md.pop('join_date')
        expiry = jd + timedelta(days=pkg.duration_days)
        member = Member.objects.create(
            **md,
            package=pkg,
            join_date=jd,
            expiry_date=expiry,
            amount_paid=0
        )
        print(f"  ✓ Member: {member.name} ({member.member_id}) — expires {member.expiry_date}")

# ── 5. CREATE EQUIPMENT ───────────────────────────
print("\n[5] Creating equipment...")

equipment_data = [
    {'serial': 'TM-001', 'name': 'Treadmill',        'brand': 'LifeFitness', 'price': 150000},
    {'serial': 'BB-001', 'name': 'Barbell Set',       'brand': 'Technogym',  'price': 45000},
    {'serial': 'DM-001', 'name': 'Dumbell Set 5-50kg','brand': 'Powerhouse', 'price': 80000},
    {'serial': 'RW-001', 'name': 'Rowing Machine',    'brand': 'Concept2',   'price': 120000},
    {'serial': 'CB-001', 'name': 'Cable Machine',     'brand': 'LifeFitness','price': 95000},
]

for ed in equipment_data:
    eq, created = Equipment.objects.get_or_create(serial=ed['serial'], defaults=ed)
    if created:
        print(f"  ✓ Equipment: {eq.name} ({eq.serial})")

print("\n" + "=" * 50)
print("SETUP COMPLETE!")
print("=" * 50)
print("\nLogin credentials:")
print("  Admin:       admin / Admin@123")
print("  Manager:     manager / Manager@123")
print("  Receptionist: reception / Recep@123")
print("  Accountant:  accountant / Acct@123")
print("\nAccess the system at: http://localhost:8000")
print("=" * 50)

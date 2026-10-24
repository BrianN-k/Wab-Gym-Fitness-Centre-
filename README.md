# WAB Gym Management System
## KCA University — STU 3101 | Kipkemboi Brian Kipkosgei (23/00574)

A web-based gym management system built with Python, Django and SQLite/MySQL.

---

## QUICK START (Windows)

### Step 1 — Install Python
Download Python 3.11 from https://python.org/downloads
✅ Check "Add Python to PATH" during installation

### Step 2 — Install Dependencies
Open Command Prompt in the project folder and run:
```
pip install django==4.2 pillow
```

### Step 3 — Setup Database
```
python manage.py migrate
```

### Step 4 — Create Admin & Sample Data
```
python manage.py shell < setup_data.py
```

### Step 5 — Run the System
```
python manage.py runserver
```

### Step 6 — Open in Browser
Go to: http://localhost:8000

---

## LOGIN CREDENTIALS

| Role         | Username    | Password     |
|--------------|-------------|--------------|
| Admin        | admin       | Admin@123    |
| Manager      | manager     | Manager@123  |
| Receptionist | reception   | Recep@123    |
| Accountant   | accountant  | Acct@123     |

---

## MYSQL PRODUCTION SETUP

1. Create database:
```sql
CREATE DATABASE wab_gym_db CHARACTER SET utf8mb4;
CREATE USER 'wabgym'@'localhost' IDENTIFIED BY 'WabGym@2026';
GRANT ALL PRIVILEGES ON wab_gym_db.* TO 'wabgym'@'localhost';
```

2. Install MySQL client:
```
pip install mysqlclient
```

3. In `wabgym/settings.py`, uncomment the MySQL DATABASES block
   and comment out the SQLite block.

4. Run migrations:
```
python manage.py migrate
python manage.py shell < setup_data.py
python manage.py runserver 0.0.0.0:8000
```

---

## PROJECT STRUCTURE

```
wabgym/
├── accounts/       User authentication & roles
├── members/        Member registration & management
├── packages/       Membership packages
├── attendance/     Employee attendance recording
├── payments/       Income & expense transactions
├── coaches/        Coach profiles & sessions
├── equipment/      Gym equipment management
├── salaries/       Employee & coach payroll
├── reports/        Dashboard & reports
├── templates/      Shared HTML templates (base.html)
├── static/         CSS, JS, images
├── wabgym/         Django project settings & URLs
├── manage.py       Django management utility
├── setup_data.py   Initial data setup script
└── requirements.txt
```

---

## SYSTEM MODULES

| Module      | Description                                    |
|-------------|------------------------------------------------|
| Dashboard   | Real-time stats, charts, expiry alerts         |
| Members     | Register, search, view, edit, deactivate       |
| Attendance  | Record & view employee attendance              |
| Transactions| Income (member payments) & expense tracking   |
| Coaches     | Coach profiles, sessions, booking             |
| Equipment   | Gym equipment inventory                        |
| Packages    | Membership plans management                   |
| Salaries    | Employee & coach payroll processing           |
| Reports     | Member, payment, attendance, payroll reports  |
| Users       | Admin-only user account management            |

---

## TECHNOLOGY STACK

- Backend:  Python 3.11, Django 4.2
- Database: SQLite (dev) / MySQL 8.0 (production)
- Frontend: Bootstrap 5, Chart.js, Bootstrap Icons
- Server:   Django dev server / Apache + mod_wsgi

---

*WAB Gym Management System v1.0 | KCA University STU 3101 | 2026*

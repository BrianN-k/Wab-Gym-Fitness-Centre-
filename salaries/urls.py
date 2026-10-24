from django.urls import path
from . import views
urlpatterns = [
    path('', views.salary_list, name='salary_list'),
    path('employee/process/', views.process_employee_salary, name='process_employee_salary'),
    path('coach/process/', views.process_coach_salary, name='process_coach_salary'),
]

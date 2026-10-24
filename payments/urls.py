from django.urls import path
from . import views
urlpatterns = [
    path('', views.payment_list, name='payment_list'),
    path('income/add/', views.debit_create, name='debit_create'),
    path('expense/add/', views.credit_create, name='credit_create'),
]

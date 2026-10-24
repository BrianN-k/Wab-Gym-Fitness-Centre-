from django.urls import path
from . import views
from .models import Member, MembershipRenewal
from decimal import Decimal

urlpatterns = [
    path('', views.member_list, name='member_list'),
    path('add/', views.member_create, name='member_create'),
    path('<int:pk>/', views.member_detail, name='member_detail'),
    path('<int:pk>/edit/', views.member_edit, name='member_edit'),
    path('<int:pk>/toggle/', views.member_toggle, name='member_toggle'),
    path('<int:pk>/renew/', views.member_renew, name='renew_member',),
    path("renew/<int:pk>/", views.member_renew, name="member_renew",),
]

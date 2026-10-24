from django.urls import path
from . import views
urlpatterns = [
    path('', views.coach_list, name='coach_list'),
    path('add/', views.coach_create, name='coach_create'),
    path('<int:pk>/', views.coach_detail, name='coach_detail'),
    path('<int:pk>/edit/', views.coach_edit, name='coach_edit'),
    path('<int:pk>/book/', views.book_session, name='book_session'),
    path('<int:pk>/toggle/', views.coach_toggle, name='coach_toggle'),
]

from django.urls import path
from . import views
urlpatterns = [
    path('', views.package_list, name='package_list'),
    path('add/', views.package_create, name='package_create'),
    path('<int:pk>/edit/', views.package_edit, name='package_edit'),
    path('<int:pk>/toggle/', views.package_toggle, name='package_toggle'),
]

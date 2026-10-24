from django.urls import path
from . import views
urlpatterns = [
    path('', views.equipment_list, name='equipment_list'),
    path('add/', views.equipment_create, name='equipment_create'),
    path('<int:pk>/toggle/', views.equipment_toggle, name='equipment_toggle'),
    path("<int:pk>/purchase/", views.add_purchase, name="add_purchase"),
]

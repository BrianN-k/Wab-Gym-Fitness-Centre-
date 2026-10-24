from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('reports.urls')),
    path('', include('accounts.urls')),
    path('members/', include('members.urls')),
    path('packages/', include('packages.urls')),
    path('attendance/', include('attendance.urls')),
    path('payments/', include('payments.urls')),
    path('coaches/', include('coaches.urls')),
    path('equipment/', include('equipment.urls')),
    path('salaries/', include('salaries.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

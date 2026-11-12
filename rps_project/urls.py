# rps_project/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('super/', admin.site.urls),
    path('attendance/', include('attendance.urls', namespace='attendance')),
    path('finance/', include('finance.urls', namespace='finance')),
    path('payroll/', include('payroll.urls', namespace='payroll')),
    path('', include('rps_app.urls')),
    path('', include('pwa.urls')),
    path('site/', include('website.urls', namespace='site')),
    path('api/', include('website.api_urls')),
]

# Only add static() in DEBUG mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

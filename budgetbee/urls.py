from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('finance.urls', 'finance'), namespace='finance')),  # <--- add namespace
    path('user/', include('userauths.urls')),  # already has app_name in userauths/urls.py
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

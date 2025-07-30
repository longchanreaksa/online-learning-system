from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')), 
    path('', include('profiles.urls')), 
#fix update employee profile
    path('courses/', include('courses.urls')),
    path('enrollments/', include('enrollments.urls')),
    path('categories/', include('categories.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
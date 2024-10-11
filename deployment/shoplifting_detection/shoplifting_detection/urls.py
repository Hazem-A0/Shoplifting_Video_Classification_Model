from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('detection.urls')),  # This will map the empty path to your detection app
]

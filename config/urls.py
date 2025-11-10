from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('main.urls')),
    path('api/auth/', include('rest_framework.urls')),
    
    # Простая корневая страница с информацией об API
    path('', include('main.urls')),  # Перенаправляем на API
]
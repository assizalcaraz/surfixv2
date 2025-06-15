from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),  # ← esta línea enruta el index    
    path('listas/', include('listas.urls')),

]

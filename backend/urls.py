from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from home import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),  
    path('listas/', include('listas.urls')),

    path('login/', auth_views.LoginView.as_view(template_name='home/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),    

]

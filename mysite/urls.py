"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib.auth import get_user_model


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # Include built-in auth URLs
    path('accounts/', include('accounts.urls')),
    path('jobs/', include('jobs.urls')),
    path('', RedirectView.as_view(url='/login/'), permanent=False),  # Redirect root URL to login page
]

User = get_user_model()
# Change these values to what you want your login to be
admin_username = 'admin'
admin_email = 'admin@example.com'
admin_password = 'Reinhard123!' 

try:
    if not User.objects.filter(username=admin_username).exists():
        User.objects.create_superuser(admin_username, admin_email, admin_password)
        print("🟢 Superuser created successfully via boot script!")
except Exception as e:
    pass
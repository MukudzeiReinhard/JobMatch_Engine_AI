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

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib.auth import get_user_model
from django.db import connection

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # Include built-in auth URLs
    path('accounts/', include('accounts.urls')),
    path('jobs/', include('jobs.urls')),
    path('', RedirectView.as_view(url='/login/', permanent=False)),  # Redirect root URL to login page
]

# ==============================================================================
# PRODUCTION MAINTENANCE BOOT SCRIPT (Temporary)
# ==============================================================================


User = get_user_model()

def run_production_maintenance():
    try:
        # 1. Force clear all django-axes lockout logs from the database tables
        with connection.cursor() as cursor:
            # We use conditional checks to prevent crashes if tables are named slightly differently
            cursor.execute("DROP TABLE IF EXISTS axes_accessattempt CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS axes_accesslog CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS axes_accessfailurelog CASCADE;")
        print("🟢 SUCCESS: Cleared all security lockout states from the database.")
    except Exception as e:
        print(f"🔴 Table clearing warning: {e}")

    try:
        # 2. Programmatically create a guaranteed fresh production administrator account
        # CRITICAL: Change these values to exactly what you want to use to log in!
        prod_username = 'masteradmin'
        prod_email = 'admin@example.com'
        prod_password = 'Reinhard@123'  # Change this to a strong password of your choice

        # Delete any existing conflicting username to avoid duplication crashes
        if User.objects.filter(username=prod_username).exists():
            User.objects.filter(username=prod_username).delete()
            
        # Create the pristine superuser account natively on PostgreSQL
        User.objects.create_superuser(prod_username, prod_email, prod_password)
        print(f"🟢 SUCCESS: Production superuser '{prod_username}' initialized natively.")
    except Exception as e:
        print(f"🔴 Superuser initialization error: {e}")

# Trigger the script execution right on server startup
run_production_maintenance()
# ==============================================================================
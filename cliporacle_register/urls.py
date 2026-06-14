"""
URL configuration for cliporacle_register project.

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
from django.http import HttpResponse
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from cliporacle_register import views

def home(request):
    return HttpResponse("Сервер запущен! Для регистрации используй /register/")
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.register_page, name='register'),
    path('login/', views.login_page, name='login'),
    path('forgot_password/', views.request_password_reset, name='forgot_password'),
    path('home/', views.home_page, name='home'),
    path('favourites/', views.favourites_page, name='favourites'),
    path('api/categories/', views.get_categories, name='get_categories'),
    path('api/videos/', views.get_videos, name='get_videos'),
    path('reset/<uidb64>/<token>/', views.reset_password_confirm, name='password_reset_confirm'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

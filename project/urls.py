"""
URL configuration for project project.

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
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from app import views

urlpatterns = [
    path('', views.login_, name='login_'),
    path('logout/', views.logout_, name='logout_'),
    path('home', views.home, name='home'),
    path('order/', views.order, name='order'),
    path('add/', views.add_book, name='add'),
    path('edit/<int:id>/', views.edit_book, name='edit'),
    path('book/<int:id>/', views.book_detail, name='book_detail'),
    path('delete/<int:id>/', views.delete_book, name='delete'),
    path('add_order/', views.add_order, name='add_order'),
    path('edit_order/<int:id>/', views.edit_order, name='edit_order'),
    path('delete_order/<int:id>/', views.delete_order, name='delete_order'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

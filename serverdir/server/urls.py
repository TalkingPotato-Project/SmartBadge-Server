"""server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path
from django.conf.urls import url, include
from rest_framework import routers
from smartbadge import views

router = routers.DefaultRouter()
router.register(r'voice-uploads', views.VoiceFileUploadViewSet)


urlpatterns = [
    path('users/', views.users_list),
    path('users/<int:pk>/', views.users),
    path('login/', views.login),
    path('location/<int:pk>/', views.location),
    path('gps-route/<int:pk>/', views.gps_route),
    path('new-route/<int:pk>/', views.new_route),
    path('change-make/<int:pk>/', views.changeMakeState),
    path('jaywalking/<int:pk>/', views.jaywalking),
    url(r'^', include(router.urls)),
    #path('safe-zone/<int:pk>/', views.safe_zone),

    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
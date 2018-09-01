from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    re_path('auth_status/([0-9]+)/', views.auth_status, name='auth_status'),
    path('validation_complete/', csrf_exempt(views.validation_complete), name='validation_complete'),
    path('logout/', views.logout, name='logout'),
]

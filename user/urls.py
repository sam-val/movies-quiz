from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from . import views
from django.contrib.auth import views as auth_views

app_name = 'user'

urlpatterns = [
    path('login/', views.MyLoginView.as_view(), name="login"),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

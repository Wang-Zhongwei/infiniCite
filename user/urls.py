from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from . import views

app_name = 'user'
urlpatterns = [
    path('', views.index, name='index'),
    path('search', views.search, name='search'),
    path('login', views.user_login, name='login'),
    path('register', views.register, name='register'),
    path('logout', auth_views.LogoutView.as_view(), name='logout')
]
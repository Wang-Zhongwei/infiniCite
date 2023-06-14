from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'user'
urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),  # create customized logout view
    path('reset/done', auth_views.PasswordResetDoneView.as_view(), name='password_reset'),
    path('reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/complete', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
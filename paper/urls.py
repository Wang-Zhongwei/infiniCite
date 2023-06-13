from django.urls import path
from . import views

app_name = 'paper'
urlpatterns =[
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('results/', views.results, name='results'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
]
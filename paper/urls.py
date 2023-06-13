from django.urls import path
from . import views

app_name = 'paper'
urlpatterns = [
    path('', views.index, name='index'),
    path('search', views.search, name='search'),
    path('autocomplete', views.autocomplete, name='autocomplete'),
    path('save', views.save_paper, name='save')
    path('search/', views.search, name='search'),
    path('results/', views.results, name='results'),
    path('graph/', views.graph, name='graph')
]
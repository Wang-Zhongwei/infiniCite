from django.urls import path
from . import views

urlpatterns =[
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('results/', views.results, name='results'),
    path('save/', views.save_paper, name='save')
]
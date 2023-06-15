from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LibraryViewSet, LibraryPaperViewSet

app_name = 'paper'
router = DefaultRouter()
router.register(r'libraries', LibraryViewSet)
urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
    path('', include(router.urls)),
    path('libraries/<int:library_pk>/papers/', LibraryPaperViewSet.as_view({'post': 'create'}), name='library-paper-add'),
    path('libraries/<int:library_pk>/papers/<str:pk>/', LibraryPaperViewSet.as_view({'delete': 'destroy'}), name='library-paper-remove'),
    path('libraries/<int:library_pk>/papers/<str:pk>/move/', LibraryPaperViewSet.as_view({'post': 'move'}), name='library-paper-move'),
]
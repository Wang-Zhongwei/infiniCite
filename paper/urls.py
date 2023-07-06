from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LibraryViewSet, LibraryPaperViewSet

app_name = 'paper'
router = DefaultRouter()
router.register(r'libraries', LibraryViewSet)
# TODO: create a separate app for the API
urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('graph/', views.graph, name='graph'),
    path('api/autocomplete/', views.autocomplete, name='autocomplete'),
    path('api/', include(router.urls)),
    path('api/libraries/<int:library_pk>/share/', LibraryViewSet.as_view({'post': 'share'}), name='library-share'),
    path('api/libraries/<int:library_pk>/papers/', LibraryPaperViewSet.as_view({'post': 'create'}), name='library-paper-add'),
    path('api/libraries/<int:library_pk>/papers/<str:pk>/', LibraryPaperViewSet.as_view({'delete': 'destroy'}), name='library-paper-remove'),
    path('api/libraries/<int:library_pk>/papers/<str:pk>/move/', LibraryPaperViewSet.as_view({'post': 'move'}), name='library-paper-move'),
]
# BEGIN: 5d8f9a2b8d7c
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LibraryViewSet, LibraryPaperViewSet
from . import views

app_name = 'paper'
router = DefaultRouter()
router.register(r'libraries', LibraryViewSet)
# TODO: add unshare endpoint
urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('graph/', views.graph, name='graph'),
    path('api/autocomplete/', views.autocomplete, name='autocomplete'),
    path('api/', include(router.urls)),
    path('api/libraries/<int:library_pk>/share/', LibraryViewSet.as_view({'post': 'share'}), name='library-share'),
    path('libraries/papers', LibraryPaperViewSet.as_view({'get': 'all_papers'}), name='library-all-papers'),
    path('libraries/<int:library_pk>/papers/', LibraryPaperViewSet.as_view({'get': 'list'}), name='library-paper-list'),
    path('api/libraries/<int:library_pk>/papers/', LibraryPaperViewSet.as_view({'post': 'create'}), name='library-paper-add'),
    path('api/libraries/<int:library_pk>/papers/<str:pk>/', LibraryPaperViewSet.as_view({'delete': 'destroy'}), name='library-paper-remove'),
    path('api/libraries/<int:library_pk>/papers/<str:pk>/move/', LibraryPaperViewSet.as_view({'post': 'move'}), name='library-paper-move'),
    path('api/paper/<str:paper_pk>/libraries/', LibraryPaperViewSet.as_view({'post': 'add_to_libraries'}), name='paper-add-to-libraries'),
]

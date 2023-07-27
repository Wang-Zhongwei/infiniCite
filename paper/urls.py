# BEGIN: 5d8f9a2b8d7c
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LibraryViewSet, LibraryPaperViewSet, PaperView, LibraryView
from . import views

app_name = "paper"
router = DefaultRouter()
router.register(r"libraries", LibraryViewSet)
# TODO: add unshare endpoint
urlpatterns = [
    path("", views.index, name="index"),
    path("search/", views.search, name="search"),
    path("graph/", views.graph, name="graph"),
    path("libraries/papers", PaperView.as_view(), name="library-all-papers"),
    path(
        "libraries/<int:library_pk>/papers/",
        LibraryView.as_view(),
        name="library-paper-list",
    ),
    path("api/", include(router.urls)),
    path("api/autocomplete/", views.autocomplete, name="autocomplete"),
    path(
        "api/libraries/<int:library_pk>/share/",
        LibraryViewSet.as_view({"post": "share", "delete": "share"}),
        name="library-share",
    ),
    path(
        "api/libraries/<int:library_pk>/papers/",
        LibraryPaperViewSet.as_view({"post": "create"}),
        name="library-paper-add",
    ),
    path(
        "api/libraries/<int:library_pk>/papers/<str:pk>/",
        LibraryPaperViewSet.as_view({"delete": "destroy"}),
        name="library-paper-remove",
    ),
    path(
        "api/libraries/<int:library_pk>/papers/<str:pk>/move/",
        LibraryPaperViewSet.as_view({"post": "move"}),
        name="library-paper-move",
    ),
    path(
        "api/paper/<str:paper_pk>/libraries/",
        LibraryPaperViewSet.as_view(
            {"post": "add_to_libraries", "delete": "remove_from_libraries"}
        ),
        name="paper-batch-operations",
    ),
    path(
        "api/paper/search/",
        LibraryPaperViewSet.as_view({"post": "search"}),  # later change to post
        name="paper-search",
    ),
    path(
        "api/paper/semantic-search/",
        LibraryPaperViewSet.as_view({"post": "semantic_search"}),
        name="paper-semantic-search",
    ),
    path(
        "api/paper/natural-language-search/",
        LibraryPaperViewSet.as_view({"post": "natural_language_search"}),
        name="paper-natural-language-search",
    ),
    path("paper/home_page.html", views.home_page, name="home_page"),
]

from django.http import JsonResponse
import requests
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from rest_framework import status, viewsets
from rest_framework.response import Response


from paper.services import PaperService
from author.services import AuthorService
from user.models import Account

from .exceptions import *

# Create your views here.
from .forms import SearchForm
from .models import Library, Paper
from .serializers import LibrarySerializer, PaperSerializer

paper_service = PaperService()
author_service = AuthorService()

def index(request):
    form = SearchForm()
    return render(request, "paper/index.html", {"form": form})


def search(request):
    if request.method == "GET":
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data["query"]
            page = form.cleaned_data["page"] or 1
            searchPaper = form.cleaned_data["searchPaper"]
            return handle_search(request, query, page, searchPaper)
        else:
            return render(request, "paper/index.html", {"form": form})
    else:
        return redirect("paper:index")


def handle_search(request, query, page, searchPaper):
    if query:
        if searchPaper:
            return search_papers(request, query, page)
        else:
            return search_authors(request, query, page)
    else:
        return redirect("paper:index")


def search_papers(request, query, page=1):
    data = paper_service.search_external_papers(query, page)
    total = data.get("total", 0)
    total_pages = total // paper_service.RECORDS_PER_PAGE + 1

    # Calculate the range of pages to show
    start = max(1, page - 3)
    end = min(total_pages, page + 3) + 1
    pages_to_show = range(start, end)

    return render(
        request,
        "paper/paper-results.html",
        {
            "papers": data,
            "page": page,
            "query": query,
            "total_pages": total_pages,
            "pages_to_show": pages_to_show,
            "searchPaper": True,
        },
    )


def search_authors(request, query, page):
    data = author_service.search_external_authors(query, page)
    total = data.get("total", 0)
    total_pages = total // author_service.RECORDS_PER_PAGE + 1

    # Calculate the range of pages to show
    start = max(1, page - 3)
    end = min(total_pages, page + 3) + 1
    pages_to_show = range(start, end)

    return render(
        request,
        "paper/author-results.html",
        {
            "authors": data,
            "page": page,
            "query": query,
            "total_pages": total_pages,
            "pages_to_show": pages_to_show,
            "searchPaper": False,
        },
    )


def autocomplete(request):
    query = request.GET.get('query')
    if query:
        # Call the API with the search input
        return JsonResponse(paper_service.autocomplete(query), safe=False)
    else:
        return redirect("index")  # redirect to index view


VALID_ORDER_BYS = ["title", "publicationDate", "citationCount", "referenceCount"]
# TODO: test order by
class LibraryView(View):
    def get(self, request, *args, **kwargs):
        library = get_object_or_404(Library, pk=kwargs["library_pk"])
        order_by = request.GET.get("order_by", "title")  # default to ordering by title
        if order_by not in VALID_ORDER_BYS:
            order_by = "title"

        papers = library.papers.order_by(order_by)
        serializer = PaperSerializer(papers, many=True)
        return render(
            request,
            "paper/library-papers.html",
            {"data": {"name": library.name, "papers": serializer.data}},
        )


class PaperView(View):
    def get(self, request, *args, **kwargs):
        account = request.user.account
        order_by = request.GET.get("order_by", "title")  # default to ordering by title
        if order_by not in VALID_ORDER_BYS:
            order_by = "title"

        papers = (
            Paper.objects.filter(libraries__owner=account).distinct().order_by(order_by)
        )
        serializer = PaperSerializer(papers, many=True)
        return render(
            request,
            "paper/library-papers.html",
            {"data": {"name": "All papers", "papers": serializer.data}},
        )


# TODO: add login required
# TODO: refactor it into three viewsets
# TODO: show saved libraries in search results?
class LibraryViewSet(viewsets.ModelViewSet):
    queryset = Library.objects.all()
    serializer_class = LibrarySerializer
    account_queryset = Account.objects.all()

    def create(self, request, *args, **kwargs):
        userId = request.user.id
        # TODO: create account when user is created
        try:
            owner = self.account_queryset.get(user_id=userId)
        except:
            # create an account if not exist
            self.account_queryset.create(user_id=userId)

        # create a library
        library = self.queryset.create(owner=owner, name=request.data["name"])
        serializer = self.serializer_class(library)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def share(self, request, *args, **kwargs):
        """
        Shares a library with an account.

        Args:
            request: The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            A Response object with a status code of 200 if the library was successfully shared, or a status code of 404 if either the library or account was not found.
        """
        library_pk = kwargs["library_pk"]
        account_id = request.data["account_id"]
        if not (library_pk and account_id):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        lib = self.queryset.get(pk=library_pk)
        acc = self.account_queryset.get(pk=account_id)
        if lib and acc:
            lib.sharedWith.add(acc)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class PaperViewSet(viewsets.ViewSet):
    queryset = Paper.objects.all()
    library_queryset = Library.objects.all()

    serializer_class = LibrarySerializer

    paper_service = PaperService()

    def create(self, request, *args, **kwargs):
        papers = [self.paper_service.get_paper_by_id(id) for id in request.data["ids"]]
        library = get_object_or_404(Library, pk=kwargs["library_pk"])
        for paper in papers:
            if paper is None:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"error": "Paper not found"},
                )
            library.papers.add(paper)
        # TODO: check if just the primary key of the paper is returned otherwise do not return data
        serializer = self.serializer_class(library)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def add_to_libraries(self, request, *args, **kwargs):
        paperId = kwargs["paper_pk"]
        paper = self.paper_service.get_paper_by_id(paperId)
        if paper is None:
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={"error": "Paper not found"}
            )

        library_ids = request.data.get("libraryIds", [])
        for library_id in library_ids:
            library = self.library_queryset.get(pk=library_id)
            library.papers.add(paper)

        return Response({"status": "success"})

    def remove_from_libraries(self, request, *args, **kwargs):
        paperId = kwargs["paper_pk"]
        paper = self.paper_service.get_paper_by_id(paperId)
        if paper is None:
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={"error": "Paper not found"}
            )

        library_ids = request.data.get("libraryIds", [])
        for library_id in library_ids:
            library = self.library_queryset.get(pk=library_id)
            library.papers.remove(paper)

        return Response({"status": "success"})

    def destroy(self, request, *args, **kwargs):
        library = get_object_or_404(Library, pk=kwargs["library_pk"])
        paper = get_object_or_404(self.queryset, pk=kwargs["pk"])
        library.papers.remove(paper)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def move(self, request, *args, **kwargs):
        source_library = get_object_or_404(Library, pk=kwargs["library_pk"])
        target_library = get_object_or_404(Library, pk=request.data["targetLibraryId"])
        paper = get_object_or_404(self.queryset, pk=kwargs["pk"])

        source_library.papers.remove(paper)
        target_library.papers.add(paper)

        source_serializer = self.serializer_class(source_library)
        target_serializer = self.serializer_class(target_library)

        return Response(
            {
                "source_library": source_serializer.data,
                "target_library": target_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

# TODO: move it to paper service class
BASE_URL = "http://api.semanticscholar.org/graph/v1"
def get_paper_info(
    paper_id, params={"fields": "paperId,authors,year,title,citationCount"}
):
    return requests.get(f"{BASE_URL}/paper/{paper_id}/", params=params).json()


def get_paper_connections(paper_id, graph_type, params={"fields": "paperId,intents"}):
    return requests.get(
        f"{BASE_URL}/paper/{paper_id}/{graph_type}", params=params
    ).json()["data"]


def create_edge(low_deg_nbr, high_deg_nbr, edge_type, graph_type):
    if graph_type == "citations":
        return {"source": high_deg_nbr, "target": low_deg_nbr, "type": edge_type}
    else:
        return {"source": low_deg_nbr, "target": high_deg_nbr, "type": edge_type}

# TODO: check if paper is in library, then show local graph using elasticsearch 
def graph(request):
    paper_id = request.GET.get("paperId", "")
    graph_type = request.GET.get("graphType", "citations")
    if graph_type == "citations":
        nbr_name = "citingPaper"
    else:
        nbr_name = "citedPaper"

    if not paper_id:
        return redirect("index")

    params = {
        "fields": "paperId,authors,year,title,citationCount,isInfluential,intents"
    }

    origin = get_paper_info(paper_id)
    first_deg_nbrs = get_paper_connections(paper_id, graph_type, params)

    nodes = [origin] + [
        {**paper[nbr_name], "isInfluencial": paper["isInfluential"]}
        for paper in first_deg_nbrs
    ]
    ids_set = set([paper["paperId"] for paper in nodes[1:]])
    edges = [
        create_edge(
            origin["paperId"],
            paper[nbr_name]["paperId"],
            paper["intents"],
            graph_type=graph_type,
        )
        for paper in first_deg_nbrs
    ]

    for first_deg_nbr in first_deg_nbrs:
        if not first_deg_nbr["isInfluential"]:
            continue
        second_deg_nbrs = get_paper_connections(
            first_deg_nbr[nbr_name]["paperId"], graph_type=graph_type
        )

        for second_deg_nbr in second_deg_nbrs:
            if second_deg_nbr[nbr_name]["paperId"] in ids_set:
                edges.append(
                    create_edge(
                        first_deg_nbr[nbr_name]["paperId"],
                        second_deg_nbr[nbr_name]["paperId"],
                        second_deg_nbr["intents"],
                        graph_type=graph_type,
                    )
                )

    for node in nodes:
        node["id"] = node.pop("paperId")

    return render(request, "paper/graph.html", {"nodes": nodes, "edges": edges})

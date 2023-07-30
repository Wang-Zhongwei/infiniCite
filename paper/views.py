from django.http import HttpResponseForbidden, JsonResponse
from elasticsearch_dsl import tokenizer
import requests
import json
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from rest_framework import status, viewsets
from rest_framework.response import Response
from author.services import AuthorService
from paper.serializers import LibrarySerializer
from paper.services import PaperService
from user.models import Account

from .exceptions import *

# Create your views here.
from .forms import SearchForm
from .models import Library, Paper
from .serializers import LibrarySerializer, PaperSerializer
from infiniCite.settings import ELASTICSEARCH_CLIENT as es
from infiniCite.settings import OPENAI_CLIENT as oa
from infiniCite.specter import tokenizer, model


from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from .models import Library

VALID_SORT_BYS = ["title", "publicationDate", "citationCount", "referenceCount"]
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
            context = search_papers(query, page)
            return render(request, "paper/paper-results.html", context)
        else:
            context = search_authors(query, page)
            return render(request, "paper/author-results.html", context)
    else:
        return redirect("paper:index")


def search_papers(query, page=1):
    data = paper_service.search_external_papers(query, page)
    total = data.get("total", 0)
    total_pages = total // paper_service.RECORDS_PER_PAGE + 1

    # Calculate the range of pages to show
    start = max(1, page - 3)
    end = min(total_pages, page + 3) + 1
    pages_to_show = range(start, end)

    return {
        "papers": data,
        "page": page,
        "query": query,
        "total_pages": total_pages,
        "pages_to_show": pages_to_show,
        "searchPaper": True,
    }


def search_authors(query, page=1):
    data = author_service.search_external_authors(query, page)
    total = data.get("total", 0)
    total_pages = total // author_service.RECORDS_PER_PAGE + 1

    # Calculate the range of pages to show
    start = max(1, page - 3)
    end = min(total_pages, page + 3) + 1
    pages_to_show = range(start, end)

    return {
        "authors": data,
        "page": page,
        "query": query,
        "total_pages": total_pages,
        "pages_to_show": pages_to_show,
        "searchPaper": False,
    }


def autocomplete(request):
    query = request.GET.get("query")
    if query:
        # Call the API with the search input
        return JsonResponse(paper_service.autocomplete(query), safe=False)
    else:
        return redirect("index")  # redirect to index view


def home_page(request):
    account = request.user.account
    libraries = Library.objects.filter(owner=account)
    list_libraryPaperRec = []
    for library in libraries:
        libraryName = library.name
        libraryPapers = library.papers.all().values()
        libraryPapersIds = []
        for paper in libraryPapers:
            libraryPapersIds.append(paper["paperId"])
        if len(libraryPapersIds) > 0:
            recommendation = getRecommendation(libraryPapersIds)
            list_libraryPaperRec.append((libraryName, recommendation))
    print(list_libraryPaperRec)
    return render(
        request, "paper/home_page.html", {"library_paper_recommendations": list_libraryPaperRec}
    )


def getRecommendation(Ids):
    RECOMMENDATION = "http://api.semanticscholar.org/recommendations/v1/papers/?limit=1&fields=authors,title,abstract,publicationTypes,url,publicationVenue"
    body = {
        "positivePaperIds": Ids,
    }
    response = requests.request("POST", RECOMMENDATION, data=json.dumps(body))
    return response.json()


def check_library_access(permission_required):
    """
    A decorator function that checks if the user has access to a library.

    Args:
        permission_required (str): The permission required to access the library. Can be "read" or "edit".

    Returns:
        function: The decorated view function.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(self, request, *args, **kwargs):
            library_pk = kwargs.get("library_pk")

            if library_pk:
                library = Library.objects.get(pk=library_pk)
                if permission_required == "read":
                    if (
                        library.owner != request.user.account
                        and request.user.account not in library.sharedWith.all()
                    ):
                        return HttpResponseForbidden(
                            "You do not have read access to this library."
                        )
                elif permission_required == "edit":
                    if library.owner != request.user.account:
                        return HttpResponseForbidden(
                            "You do not have edit access to this library."
                        )
                else:
                    return HttpResponseForbidden("Invalid permission.")

            return view_func(self, request, *args, **kwargs)

        return _wrapped_view

    return decorator


# TODO: test order by
class LibraryView(View):
    @check_library_access("read")
    def get(self, request, *args, **kwargs):
        library = get_object_or_404(Library, pk=kwargs["library_pk"])

        sort_by = request.GET.get("sort_by", "title")  # default to ordering by title
        if sort_by not in VALID_SORT_BYS:
            sort_by = "title"

        papers = library.papers.order_by(sort_by)
        serializer = PaperSerializer(papers, many=True, context={"request": request})
        return render(
            request,
            "paper/library-papers.html",
            {"data": {"name": library.name, "papers": serializer.data}},
        )


class PaperView(View):
    def get(self, request, *args, **kwargs):
        account = request.user.account
        order_by = request.GET.get("order_by", "title")  # default to ordering by title
        if order_by not in VALID_SORT_BYS:
            order_by = "title"

        papers = (
            paper_service.queryset.filter(libraries__owner=account).distinct().order_by(order_by)
        )
        serializer = PaperSerializer(papers, many=True, context={"request": request})
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
        owner = self.account_queryset.get(user_id=userId)

        # create a library
        library = self.queryset.create(owner=owner, name=request.data["name"])
        paper_ids = list(map(lambda paper: paper["paperId"], request.data.get("papers", [])))
        library.papers.set(paper_ids)

        serializer = self.serializer_class(library, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @check_library_access("edit")
    def share(self, request, *args, **kwargs):
        """
        Shares or unshares a library with an account.

        Args:
            request: The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            A Response object with a status code of 200 if the library was successfully shared or unshared, or a status code of 404 if either the library or account was not found.
        """
        library_pk = kwargs["library_pk"]
        account_id = request.data["account_id"]
        if not (library_pk and account_id):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        lib = self.queryset.get(pk=library_pk)
        acc = self.account_queryset.get(pk=account_id)
        if lib and acc:
            if request.method == "POST":
                lib.sharedWith.add(acc)
            elif request.method == "DELETE":
                lib.sharedWith.remove(acc)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class LibraryPaperViewSet(viewsets.ViewSet):
    queryset = Paper.objects.all()
    library_queryset = Library.objects.all()
    serializer_class = LibrarySerializer
    paper_service = PaperService()

    @check_library_access("edit")
    def create(self, request, *args, **kwargs):
        """
        Adds multiple papers to a library.

        Args:
            request: The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            A Response object with a status code of 201 if the papers were successfully added to the library, or a status code of 400 if any of the papers were not found.
        """
        papers = [self.paper_service.get_paper_by_id(id) for id in request.data["ids"]]
        library = get_object_or_404(Library, pk=kwargs["library_pk"])
        library.papers.add(*papers)
        # TODO: check if just the primary key of the paper is returned otherwise do not return data
        serializer = self.serializer_class(library)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def add_to_libraries(self, request, *args, **kwargs):
        paperId = kwargs["paper_pk"]
        paper = self.paper_service.get_paper_by_id(paperId)
        if paper is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Paper not found"})

        library_ids = request.data.get("libraryIds", [])
        for library_id in library_ids:
            library = self.library_queryset.get(pk=library_id)
            library.papers.add(paper)

        return Response({"status": "success"})

    @check_library_access("edit")
    def remove_from_libraries(self, request, *args, **kwargs):
        paperId = kwargs["paper_pk"]
        paper = self.paper_service.get_paper_by_id(paperId)
        if paper is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "Paper not found"})

        library_ids = request.data.get("libraryIds", [])
        for library_id in library_ids:
            library = self.library_queryset.get(pk=library_id)
            library.papers.remove(paper)

        return Response({"status": "success"})

    @check_library_access("edit")
    def destroy(self, request, *args, **kwargs):
        library = get_object_or_404(Library, pk=kwargs["library_pk"])
        paper = get_object_or_404(self.queryset, pk=kwargs["pk"])
        library.papers.remove(paper)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @check_library_access("edit")
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

    def search(self, request, *args, **kwargs):
        params = self._get_params_from_request(request)
        params.update(self._get_auth_params_from_request(request))

        hits = self._perform_search(params, is_semantic=False)
        return Response(hits, status=status.HTTP_200_OK)

    def semantic_search(self, request, *args, **kwargs):
        params = self._get_params_from_request(request)
        params.update(self._get_auth_params_from_request(request))

        hits = self._perform_search(params, is_semantic=True)
        return Response(hits, status=status.HTTP_200_OK)

    def natural_language_search(self, request, *args, **kwargs):
        prompt = request.query_params.get("prompt", None)
        if not prompt:
            raise ValueError("No message provided in the request body")

        # do traditional search first
        try:
            params = self._get_params_from_llm(prompt)
        except NoFunctionCallError as e:
            return Response(
                {
                    "error": str(e),
                    "summary": "Sorry this does not seem like a query. Try changing how you frame your question?",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )  # TODO: prompt user to modify input

        params.update(self._get_auth_params_from_request(request))

        hits = self._perform_search(params, is_semantic=False)

        summary = self.summarize_results(prompt, hits)
        return Response(
            {
                "summary": summary,
                "source": hits,
            },
            status=status.HTTP_200_OK,
        )

    def summarize_results(self, prompt, results):
        messages = [
            {
                "role": "user",
                "content": f"""Write a summary collated from this collection of key points extracted from an academic paper.
                        The summary should highlight the core argument, conclusions and evidence, and answer the user's query.\n
                        User query: {prompt}\n
                        The summary should be structured in bulleted lists following the headings Core Argument, Evidence, and Conclusions. Include url as reference if url is present. \n""",
            }
        ]

        for i, result in enumerate(results):
            messages.append(
                {
                    "role": "system",
                    "content": f"""{i + 1}-th result has score {result["_score"]}\n
                        title: {result["_source"]['title']}\n
                        abstract: {result["_source"]['abstract']}\n
                        tldr: {result["_source"]['tldr']}\n
                        url: {result["_source"]["url"]}""",
                }
            )

        response = oa.create(model="gpt-3.5-turbo", messages=messages, temperature=0.3)
        print(response)
        return response.choices[0].message.content

    def _embed_queries(self, queries):
        inputs = tokenizer(
            queries,
            padding=True,
            truncation=True,
            return_tensors="pt",
            return_token_type_ids=False,
            max_length=512,
        )

        outputs = model(**inputs)
        # take the first token in the batch as the embedding aka cls token
        embeddings = outputs.last_hidden_state[:, 0, :].detach().numpy()
        return embeddings

    def _get_auth_params_from_request(self, request):
        library_ids = request.data.get("library_ids", None)
        # only superuser can search all libraries
        is_superuser = request.user.is_superuser

        if not library_ids and not is_superuser:
            library_ids = list(
                self.library_queryset.filter(owner=request.user.account).values_list(
                    "id", flat=True
                )
            ) + list(
                self.library_queryset.filter(sharedWith=request.user.account).values_list(
                    "id", flat=True
                )
            )
        return {
            "library_ids": library_ids,
        }

    def _get_params_from_request(self, request):
        query_params = request.query_params
        query = query_params.get("query", None)
        sort_by = query_params.get("sort_by", None)
        order = query_params.get("order", "desc")

        body = request.data
        is_fuzzy = body.get("is_fuzzy", True)
        is_title_only = body.get("is_title_only", False)
        _from = body.get("from", 0)
        size = body.get("size", 10)

        if sort_by not in VALID_SORT_BYS:
            sort_by = "citationCount"  # default ordering
        elif sort_by == "title":
            sort_by = "title.keyword"

        if order not in ["asc", "desc"]:
            order = "desc"

        return {
            "query": query,
            "sort_by": sort_by,
            "order": order,
            "is_fuzzy": is_fuzzy,
            "is_title_only": is_title_only,
            "size": size,
            "from": _from,
        }

    def _get_params_from_llm(self, prompt):
        default_params = {
            "is_fuzzy": True,
            "is_title_only": False,
            "order": "desc",
            "sort_by": "citationCount",
            "from": 0,
            "size": 5,
        }

        completion = oa.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant to researchers"},
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            functions=[
                {
                    "name": "search",
                    "description": "Search function that queries elasticsearch for articles based on the given parameters",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The search query"},
                            "is_title_only": {
                                "type": "boolean",
                                "description": "Whether to search only in the title of the articles",
                            },
                            "is_fuzzy": {
                                "type": "boolean",
                                "description": "Whether to use fuzzy search or not",
                            },
                            "sort_by": {
                                "type": "string",
                                "enum": [
                                    "title.keyword",
                                    "publicationDate",
                                    "citationCount",
                                    "referenceCount",
                                ],
                                "description": "The field to sort the results by",
                            },
                            "order": {
                                "type": "string",
                                "enum": ["asc", "desc"],
                                "description": "The order to sort the results in",
                            },
                            "from": {
                                "type": "integer",
                                "description": "The index of the first result to return",
                            },
                            "size": {
                                "type": "integer",
                                "description": "The number of results to return",
                            },
                        },
                        "required": ["query"],
                    },
                }
            ],
        )
        choice = completion.choices[0]
        if choice.finish_reason == "function_call":
            default_params.update(json.loads(choice.message.function_call.arguments))
            return default_params
        else:
            raise NoFunctionCallError("No function call was made")

    def _perform_search(self, params, is_semantic):
        query = params.get("query")
        sort_by = params.get("sort_by")
        order = params.get("order")
        is_fuzzy = params.get("is_fuzzy")
        is_title_only = params.get("is_title_only")
        size = params.get("size")
        _from = params.get("from")

        library_ids = params.get("library_ids")

        query_config = {
            "_source": {
                "excludes": [
                    "embedding",
                ]
            },
            "query": {
                "bool": {
                    "must": [
                        {
                            "nested": {
                                "path": "libraries",
                                "query": {
                                    "bool": {
                                        "filter": {
                                            "terms": {"libraries.id": library_ids, "boost": 0.0}
                                        }
                                    },
                                },
                            },
                        }
                        if library_ids
                        else {"match_all": {"boost": 0.0}},
                    ],
                    "should": [],
                }
            },
            "size": size,
            "from": _from,
            "sort": [
                {"_score": {"order": "desc"}},
                {sort_by: {"order": order}},
            ],
        }

        if is_semantic:
            embedding = self._embed_queries([query])
            query_config["query"]["bool"]["must"].extend(
                [
                    {"exists": {"field": "embedding", "boost": 0.0}},
                    {
                        "script_score": {
                            "query": {"match_all": {}},
                            "script": {
                                "source": "(cosineSimilarity(params.query_vector, 'embedding') + 1.0) / 2.0",
                                "params": {"query_vector": list(embedding[0])},
                            },
                        },
                    },
                ]
            )
        else:
            query_config["query"]["bool"]["should"].extend(
                [
                    {
                        "multi_match": {
                            "query": query,
                            "fields": [
                                "title",
                                "abstract",
                                "tldr",
                            ],
                            "fuzziness": "AUTO" if is_fuzzy else 0,
                            "boost": 0.6,
                        }
                    },
                    {
                        "nested": {
                            "path": "authors",
                            "query": {
                                "match": {
                                    "authors.name": {
                                        "query": query,
                                        "fuzziness": "AUTO" if is_fuzzy else 0,
                                    }
                                }
                            },
                            "boost": 0.4,
                        }
                    },
                ]
                if not is_title_only
                else [{"match": {"title": {"query": query, "fuzziness": "AUTO"}}}],
            )
            query_config["highlight"] = {
                "fields": {
                    "title": {},
                    "abstract": {},
                    "tldr": {},
                    "authors.name": {},
                }
            }

        results = es.search(index="paper-index", body=query_config)
        return results["hits"]["hits"]


# TODO: move it to paper service class
BASE_URL = "http://api.semanticscholar.org/graph/v1"


def get_paper_info(paper_id, params={"fields": "paperId,authors,year,title,citationCount"}):
    return requests.get(f"{BASE_URL}/paper/{paper_id}/", params=params).json()


def get_paper_connections(paper_id, graph_type, params={"fields": "paperId,intents"}):
    return requests.get(f"{BASE_URL}/paper/{paper_id}/{graph_type}", params=params).json()["data"]


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

    params = {"fields": "paperId,authors,year,title,citationCount,isInfluential,intents"}

    origin = get_paper_info(paper_id)
    first_deg_nbrs = get_paper_connections(paper_id, graph_type, params)

    nodes = [origin] + [
        {**paper[nbr_name], "isInfluencial": paper["isInfluential"]} for paper in first_deg_nbrs
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

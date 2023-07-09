from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# Create your views here.
from .forms import SearchForm
import requests
from django.http import JsonResponse
from user.models import Account
from .models import Paper, Library
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Library, Paper
from .serializers import LibrarySerializer, PaperSerializer
from user.serializers import AccountSerializer
from .exceptions import *

BASE_URL = 'http://api.semanticscholar.org/graph/v1'
RECORDS_PER_PAGE = 10
def index(request):
    form = SearchForm()
    return render(request, 'paper/index.html', {'form': form})

def search(request):
    if request.method == "GET":
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            page = form.cleaned_data['page'] or 1
            searchPaper = form.cleaned_data['searchPaper']
            return handle_search(request, query, page, searchPaper)
        else:
            return render(request, 'paper/index.html', {'form': form})
    else:
        return redirect('paper:index')


def handle_search(request, query, page, searchPaper):
    if query:
        if searchPaper:
            return search_papers(request, query, page)
        else:
            return search_authors(request, query, page)
    else:
        return redirect('paper:index')

    
def search_papers(request, query, page):
    params = {
        'query': query,
        'limit': RECORDS_PER_PAGE,
        'offset': (page - 1) * RECORDS_PER_PAGE,
        'fields': 'paperId,title,abstract,year,publicationTypes,journal,publicationVenue,referenceCount,citationCount,url,fieldsOfStudy,authors'
    }
    response = requests.get(f'{BASE_URL}/paper/search', params=params)
    data = response.json()
    total = data.get('total', 0)
    total_pages = total // RECORDS_PER_PAGE + 1

    # Calculate the range of pages to show
    start = max(1, page - 3)
    end = min(total_pages, page + 3) + 1
    pages_to_show = range(start, end)

    return render(request, 'paper/paper-results.html', {'papers': data, 'page': page, 'query': query, 'total_pages': total_pages, 'pages_to_show': pages_to_show, 'searchPaper': True})


def search_authors(request, query, page):
    params = {
        'query': query,
        'limit': RECORDS_PER_PAGE,
        'offset': (page - 1) * RECORDS_PER_PAGE,
        'fields': 'authorId,name,affiliations,paperCount,citationCount,hIndex'
    }
    response = requests.get(f'{BASE_URL}/author/search', params=params)
    data = response.json()
    total = data.get('total', 0)
    total_pages = total // RECORDS_PER_PAGE + 1

    # Calculate the range of pages to show
    start = max(1, page - 3)
    end = min(total_pages, page + 3) + 1
    pages_to_show = range(start, end)

    return render(request, 'paper/author-results.html', {'authors': data, 'page': page, 'query': query, 'total_pages': total_pages, 'pages_to_show': pages_to_show, 'searchPaper': False})

def autocomplete(request):
    query = request.GET.get('query', '')
    print('query', query)
    if query:
        # Call the API with the search input
        params = {
            'query': query,
        }
        response = requests.get(f'{BASE_URL}/paper/autocomplete', params=params)
        return JsonResponse(response.json(), safe=False)
    else:
        return redirect('index')  # redirect to index view

# TODO: add login required
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
        library = self.queryset.create(owner=owner, name=request.data['name'])
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
        library_pk = kwargs['library_pk']
        account_id = request.data['account_id']
        if not (library_pk and account_id):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        lib = self.queryset.get(pk=library_pk)
        acc = self.account_queryset.get(pk=account_id)
        if lib and acc:
            lib.sharedWith.add(acc)
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

class LibraryPaperViewSet(viewsets.ViewSet):
    library_queryset = Library.objects.all()
    queryset = Paper.objects.all()
    serializer_class = LibrarySerializer
    paper_query_params = {
        'fields': 'paperId,title,abstract,year,journal,publicationTypes,publicationVenue,referenceCount,citationCount,url,fieldsOfStudy,authors,embedding,tldr,openAccessPdf,publicationDate',
    }

    def create(self, request, *args, **kwargs):
        papers = [self.get_paper(id) for id in request.data['ids']]
        library = get_object_or_404(Library, pk=kwargs['library_pk'])
        for paper in papers:
            if paper is None:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Paper not found'})
            library.papers.add(paper)
        # TODO: check if just the primary key of the paper is returned otherwise do not return data
        serializer = self.serializer_class(library)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get_paper(self, id):
        try:
            paper = self.queryset.get(paperId=id)
        except Paper.DoesNotExist:
            # If the paper doesn't exist in the library, use the Semantic Scholar API to search for the paper
            try: 
                paper = self.get_paper_thru_api(id)
            except SemanticAPIException:
                return None
            
        return paper

    # def add_to_libraries(self, request, *args, **kwargs):
    #     paperId = kwargs['paper_pk']
    #     paper = self.get_paper(paperId)
    #     if paper is None:
    #         return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Paper not found'})

    #     library_ids = request.data.get('ids', [])
    #     paper = self.get_object()
    #     for library_id in library_ids:
    #         library = self.library_queryset.get(pk=library_id)
    #         library.papers.add(paper)

    #     return Response({'status': 'success'})
    
    def get_paper_thru_api(self, id, save=True):
        response = requests.get(f'{BASE_URL}/paper/{id}', params=self.paper_query_params)

        if response.status_code != 200:
            # You might want to add more specific error handling here
            raise SemanticAPIException(f'Semantic API returned status code {response.status_code}')

        paper_data = response.json()
        paper = self.queryset.create(
            paperId=paper_data['paperId'],
            url=paper_data['url'],
            title=paper_data['title'],
            abstract=paper_data['abstract'] if paper_data['abstract'] is not None else '',
            referenceCount=paper_data['referenceCount'],
            citationCount=paper_data['citationCount'],
            openAccessPdf = paper_data['openAccessPdf']['url'] if paper_data['openAccessPdf'] is not None else '',
            embedding=paper_data['embedding']['vector'] if paper_data['embedding'] is not None else [],
            tldr=paper_data['tldr']['text'] if paper_data['tldr'] is not None else '',
            publicationDate=paper_data['publicationDate'],
            # TODO: handle authors saving in the database
        )
        if save:
            paper.save()
        return paper

    def destroy(self, request, *args, **kwargs):
        library = get_object_or_404(Library, pk=kwargs['library_pk'])
        paper = get_object_or_404(self.queryset, pk=kwargs['pk'])
        library.papers.remove(paper)
        return Response(status=status.HTTP_204_NO_CONTENT)
        
    def move(self, request, *args, **kwargs):
        source_library = get_object_or_404(Library, pk=kwargs['library_pk'])
        target_library = get_object_or_404(Library, pk=request.data['targetLibraryId'])
        paper = get_object_or_404(self.queryset, pk=kwargs['pk'])

        source_library.papers.remove(paper)
        target_library.papers.add(paper)

        source_serializer = self.serializer_class(source_library)
        target_serializer = self.serializer_class(target_library)
        
        return Response({
            'source_library': source_serializer.data,
            'target_library': target_serializer.data,
        }, status=status.HTTP_200_OK)
    
def get_paper_info(paper_id, params={'fields': 'paperId,authors,year,title,citationCount'}):
    return requests.get(f'{BASE_URL}/paper/{paper_id}/', params=params).json()

def get_paper_connections(paper_id, graph_type, params={'fields': 'paperId,intents'}):
    return requests.get(f'{BASE_URL}/paper/{paper_id}/{graph_type}', params=params).json()['data']

def create_edge(low_deg_nbr, high_deg_nbr, edge_type, graph_type):
    if graph_type == 'citations':
        return {"source": high_deg_nbr, "target": low_deg_nbr, "type":edge_type}
    else:
        return {"source": low_deg_nbr, "target": high_deg_nbr, "type":edge_type}


def graph(request):
    paper_id = request.GET.get('paperId', '')
    graph_type = request.GET.get('graphType', 'citations')
    if graph_type == 'citations':
        nbr_name = 'citingPaper'
    else:
        nbr_name = 'citedPaper'
    
    if not paper_id:
        return redirect('index')

    params = {'fields': 'paperId,authors,year,title,citationCount,isInfluential,intents'}
    
    origin = get_paper_info(paper_id)
    first_deg_nbrs = get_paper_connections(paper_id, graph_type, params)

    nodes = [origin] + [{**paper[nbr_name], "isInfluencial": paper['isInfluential']} for paper in first_deg_nbrs]
    ids_set = set([paper['paperId'] for paper in nodes[1:]])
    edges = [create_edge(origin['paperId'], paper[nbr_name]['paperId'], paper['intents'], graph_type=graph_type) for paper in first_deg_nbrs]

    for first_deg_nbr in first_deg_nbrs:
        if not first_deg_nbr['isInfluential']:
            continue
        second_deg_nbrs = get_paper_connections(first_deg_nbr[nbr_name]['paperId'], graph_type=graph_type)

        for second_deg_nbr in second_deg_nbrs:
            if second_deg_nbr[nbr_name]['paperId'] in ids_set:
                edges.append(create_edge(first_deg_nbr[nbr_name]['paperId'], second_deg_nbr[nbr_name]['paperId'],  second_deg_nbr['intents'], graph_type=graph_type))

    for node in nodes:
        node['id'] = node.pop('paperId')

    return render(request, 'paper/graph.html', {'nodes': nodes, 'edges': edges})

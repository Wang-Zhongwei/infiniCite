from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# Create your views here.
from .forms import SearchForm
import requests
from django.http import JsonResponse
from user.models import Account
from .models import Paper, Library

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
        'fields': 'paperId,title,abstract,year,referenceCount,citationCount,url,fieldsOfStudy,authors'
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

@login_required
def save_paper(request):
    paperId = request.GET.get('paperId')
    
    if paperId:
        try:
            paper = Paper.objects.get(id=paperId)
        except:
            pass
    return JsonResponse({'status':'ok'})

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Library, Paper
from .serializers import LibrarySerializer, PaperSerializer


class LibraryViewSet(viewsets.ModelViewSet):
    queryset = Library.objects.all()
    serializer_class = LibrarySerializer
    def create(self, request, *args, **kwargs):
        userId = request.user.id
        # try get the account by user_id 
        try: 
            owner = Account.objects.get(user_id=userId)
        except:
            # create an account if not exist
            owner = Account.objects.create(user_id=userId)
        # create a library
        library = Library.objects.create(owner=owner, name=request.data['name'])
        serializer = LibrarySerializer(library)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class LibraryPaperViewSet(viewsets.ViewSet):
    def create(self, request, *args, **kwargs):
        library = get_object_or_404(Library, pk=kwargs['library_pk'])
        
        # Try to get the paper from the library
        try:
            paper = Paper.objects.get(paperId=request.data['paperId'])
        except Paper.DoesNotExist:
            # If the paper doesn't exist in the library, use the Semantic Scholar API to search for the paper
            query_params = {
                'fields': 'paperId,title,abstract,year,referenceCount,citationCount,url,fieldsOfStudy,authors,embedding,tldr,openAccessPdf,publicationDate',
            }
            paper = self.get_paper_by_id(request.data['paperId'], query_params)
            if paper is None:
                return Response({'detail': 'Paper not found.'}, status=status.HTTP_404_NOT_FOUND)

        library.papers.add(paper)
        serializer = LibrarySerializer(library)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get_paper_by_id(self, id, query_params):
        response = requests.get(f'{BASE_URL}/paper/{id}', params=query_params)

        if response.status_code != 200:
            # You might want to add more specific error handling here
            return None

        paper_data = response.json()

        try:
            paper = Paper.objects.create(
                paperId=paper_data['paperId'],
                url=paper_data['url'],
                title=paper_data['title'],
                abstract=paper_data.get('abstract', ""),
                referenceCount=paper_data['referenceCount'],
                citationCount=paper_data['citationCount'],
                openAccessPdf=paper_data['openAccessPdf'].get('url', ""),
                embedding=paper_data['embedding'].get('vector', []),
                tldr=paper_data['tldr'].get('text', ""),
                publicationDate=paper_data['publicationDate'],
                # You'll need to handle authors separately
            )
        except KeyError:
            # Handle the case where expected data was not found in the response
            return None

        return paper

    def destroy(self, request, *args, **kwargs):
        library = get_object_or_404(Library, pk=kwargs['library_pk'])
        paper = get_object_or_404(Paper, pk=kwargs['pk'])
        library.papers.remove(paper)
        return Response(status=status.HTTP_204_NO_CONTENT)
        
    def move(self, request, *args, **kwargs):
        source_library = get_object_or_404(Library, pk=kwargs['library_pk'])
        target_library = get_object_or_404(Library, pk=request.data['targetLibraryId'])
        paper = get_object_or_404(Paper, pk=kwargs['pk'])

        source_library.papers.remove(paper)
        target_library.papers.add(paper)

        source_serializer = LibrarySerializer(source_library)
        target_serializer = LibrarySerializer(target_library)
        
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

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# Create your views here.
from .forms import SearchForm
import requests
from django.http import JsonResponse

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
            page = form.cleaned_data['page']
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
    return render(request, 'paper/paper_results.html', {'papers': response.json()})


def search_authors(request, query, page):
    params = {
        'query': query,
        'limit': RECORDS_PER_PAGE,
        'offset': (page - 1) * RECORDS_PER_PAGE,
        'fields': 'authorId,name,affiliations,paperCount,citationCount,hIndex'
    }
    response = requests.get(f'{BASE_URL}/author/search', params=params)
    return render(request, 'paper/author_results.html', {'authors': response.json()})

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

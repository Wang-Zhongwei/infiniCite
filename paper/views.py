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
    
def graph(request):
    paperId = request.session.get('query')
    if paperId:
        params = {
            'fields' : 'paperId,authors,year'
        }
        #Call the API to get the info about this paper
        originalPaper = requests.get(f'{BASE_URL}/{paperId}/',params=params)
        # Call the API to get the references and citations
        citations = requests.get(f'{BASE_URL}/{paperId}/citations',params=params)
        references = requests.get(f'{BASE_URL}/{paperId}/references',params=params)
        citationNodes = list()
        citationEdges = list()
        
        citationNodes.append(originalPaper)
        for paper in citations.json()['data']:
            citationNodes.append(paper)
        for currentPaper in citationNodes[1:]: #Start at the second list element so we don't draw an edge from this paper to itself
            newEdge = [originalPaper, currentPaper]
            citationEdges.append(newEdge)
            currentPaperCitations = requests.get(f'{BASE_URL}/{currentPaper["paperId"]}/citations',params=params)
            for possiblePaper in currentPaperCitations.json()['data']:
                for citedPaper in citationNodes:
                    if possiblePaper['paperId'] == citedPaper['paperId']:
                        newEdge = [currentPaper,possiblePaper]
                        citationEdges.append(newEdge)
        


        # Render the results as a graph with connections
        return render(request, 'graph.html', {'nodes': citationNodes, 'edges': citationEdges})
    else:
        return redirect('index') # Redirect to index view

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
<<<<<<< HEAD

@login_required
def save_paper(request):
    paper_id = request.POST.get('id')
    action = request.POST.get('action')
    
    if paper_id and action:
        try:
            paper = paper.objects.get(id=paper_id)
            if action == 'save':
                paper.users_saved.add(id=paper_id)
            else:
                paper.users_saved.remove(id=paper_id)
            return JsonResponse({'status':'ok'})
        except:
            pass
    return JsonResponse({'status':'ok'})
=======
    
def graph(request):
    query = request.session.get('query')
    print(query)
    if query:
        #request.session['query'] = None
        # Call the API to get the references and citations
        params = {
            'fields': 'citations,references'
        }
        response = requests.get(f'{BASE_URL}/{request.session["query"]}', params=params)
        # Render the results as a graph with connections
        return render(request, 'graph.html', {'paper': response.json()})
    #Not sure what this does quite yet- need to figure it out
    else:
        return redirect('index') # Redirect to index view
>>>>>>> 6284ab7 (First few features)

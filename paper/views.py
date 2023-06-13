from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# Create your views here.
from .forms import SearchForm
import requests
from django.http import JsonResponse

BASE_URL = 'http://api.semanticscholar.org/graph/v1/paper'
def index(request):
    form = SearchForm()
    return render(request, 'index.html', {'form': form})

def search(request):
    if request.method == "GET":
        form = SearchForm(request.GET)
        if form.is_valid():
            # Store the search input in session
            request.session['query'] = form.cleaned_data['query']
            return redirect('results')  # redirect to results view
        else:
            return render(request, 'index.html', {'form': form})
    return redirect('index')  # redirect to index view

def results(request):
    query = request.session.get('query')
    if query:
        request.session['query'] = None
        # Call the API with the search input
        params = {
            'query': query,
            'fields': 'paperId,title,abstract,year,referenceCount,citationCount,url,fieldsOfStudy'
        }
        response = requests.get(f'{BASE_URL}/search', params=params)
        # Render the results in another page
        return render(request, 'results.html', {'papers': response.json()})
    else:
        return redirect('index')  # redirect to index view

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
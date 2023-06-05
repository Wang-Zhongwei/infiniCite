from django.shortcuts import render, redirect

# Create your views here.
from .forms import SearchForm
import requests

# get called when client requests /search
def search(request):
    if request.method == "GET":
        form = SearchForm(request.GET)
        if form.is_valid():
            # Store the search input in session
            request.session['search_input'] = form.cleaned_data['search_input']
            return redirect('results')
    else:
        form = SearchForm()

    return render(request, 'search.html', {'form': form})

# get called when client requests /results
def results(request):
    search_input = request.session.get('search_input')
    if search_input:
        # Call the API with the search input
        response = requests.get(f'http://api.crossref.org/works?query={search_input}')
        # Render the results in another page
        return render(request, 'results.html', {'data': response.json()})
    else:
        return redirect('search')

from django import forms

class SearchForm(forms.Form):
    search_input = forms.CharField(max_length=200)
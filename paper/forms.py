from typing import Any, Mapping, Optional, Type, Union
from django import forms
from django.forms.utils import ErrorList

class SearchForm(forms.Form):
    query = forms.CharField(max_length=200)
    page = forms.IntegerField(min_value=1, initial=1)
    searchPaper = forms.BooleanField(required=False, initial=True)

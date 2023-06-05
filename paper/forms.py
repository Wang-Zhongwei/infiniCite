from typing import Any, Mapping, Optional, Type, Union
from django import forms
from django.forms.utils import ErrorList

class SearchForm(forms.Form):
    query = forms.CharField(max_length=200)

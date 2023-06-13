import requests
import json

params = {
            'fields': 'citations,references'
        }
response = requests.get('http://api.semanticscholar.org/graph/v1/paper/18305cc15dd15e7cc79d1a0ef332f8e5e822e513', params=params)
print(response.json())
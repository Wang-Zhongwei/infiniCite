import requests
import json

#Generate temporary data for the database

response = requests.get("http://api.semanticscholar.org/graph/v1/paper/search?query=literature+graph")
outfile = "SampleData.json"
with open(outfile, "w") as filename:
    data = list()
    data = response.json()['data']
    for item in data:
        id = item['paperId']
        newResponse = requests.get("http://api.semanticscholar.org/graph/v1/paper/" + str(id) + "?fields=title,citations,authors,year,abstract")
        print(filename.write(json.dumps(newResponse.json()) + "\n"))
        recursiveData = newResponse.json()['citations']
        for item in recursiveData:
            recursiveId = item['paperId']
            recursiveNewResponse = requests.get("http://api.semanticscholar.org/graph/v1/paper/" + str(recursiveId) + "?fields=title,citations,authors,year,abstract")
            print(filename.write(json.dumps(recursiveNewResponse.json()) + "\n"))
        
    



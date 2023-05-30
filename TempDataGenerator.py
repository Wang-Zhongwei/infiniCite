import requests
import json

#Generate temporary data for the database

response = requests.get("http://api.semanticscholar.org/graph/v1/paper/search?query=literature+graph")
outfile = "SampleData.json"
finalOutput = list()
with open(outfile, "w") as filename:
    data = list()
    print(response.json()['data'])
    data = response.json()['data']
    for item in data:
        id = item['paperId']
        newResponse = requests.get("http://api.semanticscholar.org/graph/v1/paper/" + str(id) + "?fields=title,citations,authors,year,abstract")
        print(newResponse)
        finalOutput.append(newResponse.json())
        
        
        recursiveData = newResponse.json()['citations']
        for item in recursiveData:
            recursiveId = item['paperId']
            recursiveNewResponse = requests.get("http://api.semanticscholar.org/graph/v1/paper/" + str(recursiveId) + "?fields=title,citations,authors,year,abstract")
            finalOutput.append(recursiveNewResponse.json())
            print(recursiveNewResponse)
    
    #filename.write(json.dumps(finalOutput))
    json.dump(finalOutput,filename)
        
        
    



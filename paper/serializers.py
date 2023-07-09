from rest_framework import serializers
from .models import Library, Paper

class PaperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paper
        fields = ['paperId', 'url', 'title', 'abstract', 'referenceCount', 
                  'citationCount', 'openAccessPdf',
                  'publicationDate', 'authors', 'publicationVenue', 'publicationTypes']

class LibrarySerializer(serializers.ModelSerializer):
    papers = PaperSerializer(many=True, read_only=True)
    
    class Meta:
        model = Library
        fields = ['id', 'name', 'owner', 'papers', 'sharedWith']

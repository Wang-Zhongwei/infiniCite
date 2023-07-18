from rest_framework import serializers
from .models import Library, Paper

class PaperLibrarySerializer(serializers.ModelSerializer):
    class Meta: 
        model = Library 
        fields = ['id', 'name']

class PaperSerializer(serializers.ModelSerializer):
    libraries = PaperLibrarySerializer(many=True, read_only=True)
    class Meta:
        model = Paper
        fields = ['paperId', 'url', 'title', 'abstract', 'referenceCount', 
                  'citationCount', 'openAccessPdf',
                  'publicationDate', 'authors', 'publicationVenue', 'publicationTypes', 'fieldsOfStudy', 'libraries']

class LibrarySerializer(serializers.ModelSerializer):
    papers = PaperSerializer(many=True, read_only=True)
    
    class Meta:
        model = Library
        fields = ['id', 'name', 'owner', 'papers', 'sharedWith']

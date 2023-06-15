from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Author

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['authorId', 'externalIds', 'name', 'affiliations', 
                  'paperCount', 'citationCount', 'hIndex']
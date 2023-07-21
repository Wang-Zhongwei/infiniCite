from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Author, PublicationVenue


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = [
            "authorId",
            "externalIds",
            "name",
            "affiliations",
            "paperCount",
            "citationCount",
            "hIndex",
        ]


class SimpleAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["authorId", "name"]


class PublicationVenueSerialzier(serializers.ModelSerializer):
    class Meta:
        model = PublicationVenue
        fields = ["id", "name", "type", "url", "alternate_names"]


class SimplePublicationVenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicationVenue
        fields = ["id", "name", "url"]

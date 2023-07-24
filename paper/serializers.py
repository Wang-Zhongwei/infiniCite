from os import read
from rest_framework import serializers
from django.db.models import Q
from author.serializers import SimpleAuthorSerializer, SimplePublicationVenueSerializer

from .models import Library, Paper


class SimpleLibrarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Library
        fields = ["id", "name"]


class PaperSerializer(serializers.ModelSerializer):
    libraries = serializers.SerializerMethodField()
    authors = SimpleAuthorSerializer(many=True, read_only=True)
    publicationVenue = SimplePublicationVenueSerializer(read_only=True)

    class Meta:
        model = Paper
        fields = [
            "paperId",
            "url",
            "title",
            "abstract",
            "referenceCount",
            "citationCount",
            "openAccessPdf",
            "publicationDate",
            "authors",
            "publicationVenue",
            "publicationTypes",
            "fieldsOfStudy",
            "libraries",
        ]

    def get_libraries(self, obj):
        request = self.context.get("request")
        return SimpleLibrarySerializer(
            obj.libraries.filter(Q(owner__user=request.user) | Q(sharedWith__user=request.user)),
            many=True,
            read_only=True,
        ).data


class LibrarySerializer(serializers.ModelSerializer):
    papers = PaperSerializer(many=True, read_only=True)

    class Meta:
        model = Library
        fields = ["id", "name", "owner", "papers", "sharedWith"]

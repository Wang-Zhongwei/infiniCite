from rest_framework import serializers

from author.serializers import SimpleAuthorSerializer, SimplePublicationVenueSerializer

from .models import Library, Paper


class SimpleLibrarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Library
        fields = ["id", "name"]


class PaperSerializer(serializers.ModelSerializer):
    libraries = SimpleLibrarySerializer(many=True, read_only=True)
    authors = SimpleAuthorSerializer(many=True, read_only=True)
    publicationVenue = SimplePublicationVenueSerializer()

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


class LibrarySerializer(serializers.ModelSerializer):
    papers = PaperSerializer(many=True, read_only=True)

    class Meta:
        model = Library
        fields = ["id", "name", "owner", "papers", "sharedWith"]

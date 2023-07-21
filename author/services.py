import os

import requests

from author.models import Author, PublicationVenue
from paper.exceptions import SemanticAPIException


class AuthorService:
    BASE_URL = "http://api.semanticscholar.org/graph/v1/author"
    queryset = Author.objects.all()
    FULL_AUTHOR_FIELDS = "authorId,name,affiliations,paperCount,citationCount,hIndex"
    BASIC_AUTHOR_FIELDS = "authorId,name"
    RECORDS_PER_PAGE = 15

    def get_author_or_create(
        self, author_data, should_save=True, is_simple_author=True
    ):
        if is_simple_author:
            author = self.queryset.get_or_create(
                authorId=author_data["authorId"],
                name=author_data["name"],
            )[0]
        else:
            try:
                author = self.get_external_author_by_id(
                    author_data["authorId"], should_save
                )
            except SemanticAPIException:
                return None
        return author

    def get_external_author_by_id(self, id, should_save=True):
        if not id:
            raise ValueError("Author ID cannot be empty")

        response = requests.get(
            os.path.join(self.BASE_URL, id), params={"fields": self.FULL_AUTHOR_FIELDS}
        )

        if response.status_code != 200:
            raise SemanticAPIException(
                f"Semantic API returned status code {response.status_code}"
            )

        author_data = response.json()

        if not author_data:
            raise SemanticAPIException("No author data found")

        author = self.queryset.get_or_create(
            authorId=author_data["authorId"],
            name=author_data["name"],
        )[0]

        if "affiliations" in author_data:
            author.affiliations = author_data["affiliations"]

        if "paperCount" in author_data:
            author.paperCount = author_data["paperCount"]

        if "citationCount" in author_data:
            author.citationCount = author_data["citationCount"]

        if "hIndex" in author_data:
            author.hIndex = author_data["hIndex"]

        if should_save:
            author.save()

        return author

    def search_external_authors(self, query, page):
        params = {
            "query": query,
            "limit": self.RECORDS_PER_PAGE,
            "offset": (page - 1) * self.RECORDS_PER_PAGE,
            "fields": self.FULL_AUTHOR_FIELDS,
        }
        return requests.get(
            os.path.join(self.BASE_URL, "search"),
            params=params,
        ).json()


class PublicationVenueService:
    queryset = PublicationVenue.objects.all()

    def get_publicationVenue_or_create(self, data):
        return self.queryset.get_or_create(
            id=data["id"],
            name=data["name"],
            type=data.get("type", None),
            alternate_names=data.get("alternate_names", None),
            url=data.get("url", None),
        )[0]

import json
import os

import requests

from author.models import Author, PublicationVenue
from paper.exceptions import SemanticAPIException
from paper.models import Paper


class AuthorService:
    BASE_URL = "http://api.semanticscholar.org/graph/v1/author"
    queryset = Author.objects.all()
    BASIC_AUTHOR_FIELDS = "authorId,name"
    NO_NESTED_FIELDS = "authorId,name,affiliations,paperCount,citationCount,hIndex"
    FULL_AUTHOR_FIELDS = NO_NESTED_FIELDS + ",papers"
    RECORDS_PER_PAGE = 15

    def get_external_author_by_id(self, id):
        if not id:
            raise ValueError("Author ID cannot be empty")

        response = requests.get(
            os.path.join(self.BASE_URL, id), params={"fields": self.FULL_AUTHOR_FIELDS}
        )

        if response.status_code != 200:
            raise SemanticAPIException(
                response.status_code, f"Semantic API returned status code {response.status_code}"
            )

        author_data = response.json()

        if not author_data:
            raise SemanticAPIException(response.status_code, "No author data found")

        author = self.queryset.get_or_create(
            authorId=author_data["authorId"],
        )[0]

        self.assign_data_to_author(author, author_data, True)

        return author

    def assign_data_to_author(self, author, author_data, including_nested_fields):
        if "name" in author_data:
            author.name = author_data["name"]

        if "affiliations" in author_data:
            author.affiliations = author_data["affiliations"]

        if "paperCount" in author_data:
            author.paperCount = author_data["paperCount"]

        if "citationCount" in author_data:
            author.citationCount = author_data["citationCount"]

        if "hIndex" in author_data:
            author.hIndex = author_data["hIndex"]

        if including_nested_fields:
            papers_data = list(
                filter(
                    lambda x: x["paperId"] is not None and x["title"] is not None,
                    author_data["papers"],
                )
            )
            papers_ids = [paper["paperId"] for paper in papers_data]
            existing_papers = author.papers.filter(paperId__in=papers_ids)
            existing_paper_ids = set([paper.paperId for paper in existing_papers])
            new_papers = author.papers.bulk_create(
                [
                    Paper(paperId=paper["paperId"], title=paper["title"])
                    for paper in papers_data
                    if paper["paperId"] not in existing_paper_ids
                ]
            )

            # add papers to author
            author.papers.add(*existing_papers, *new_papers)

        return author
    
    def save_external_author_by_id(self, id):
        author = self.get_external_author_by_id(id)
        author.save()

    def save_external_author_by_id(self, id):
        author = self.get_external_author_by_id(id)
        author.save()

    def get_external_authors_by_ids(self, ids, including_nested_fields=False):
        if including_nested_fields:
            params = {"fields": self.FULL_AUTHOR_FIELDS}
        else:
            params = {"fields": self.NO_NESTED_FIELDS}

        payload = json.dumps({"ids": ids})
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            os.path.join(self.BASE_URL, "batch"),
            params=params,
            data=payload,
            headers=headers,
        )
        if response.status_code != 200:
            raise SemanticAPIException(
                response.status_code, f"Semantic API returned status code {response.status_code}"
            )

        authors_data = response.json()
        authors = []
        for i, author_data in enumerate(authors_data):
            if not author_data:
                raise SemanticAPIException(
                    response.status_code, f"No author data found for author {ids[i]}"
                )
            author = self.queryset.get_or_create(
                authorId=author_data["authorId"],
            )[0]
            self.assign_data_to_author(author, author_data, including_nested_fields)
            authors.append(author)
        return authors

    def save_external_authors_by_ids(self, ids, including_nested_fields=False):
        authors = self.get_external_authors_by_ids(ids, including_nested_fields)
        self.queryset.bulk_update(
            authors, ["name", "affiliations", "paperCount", "citationCount", "hIndex"]
        )

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

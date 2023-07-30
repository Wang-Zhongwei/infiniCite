import json
import os
import requests
from author.models import Author
from author.services import AuthorService, PublicationVenueService

from paper.exceptions import SemanticAPIException
from paper.models import Paper


class AuthorService:
    BASE_URL = "http://api.semanticscholar.org/graph/v1/paper"
    queryset = Paper.objects.all()
    RECORDS_PER_PAGE = 10
    BASIC_PAPER_FIELDS = "paperId,title,abstract,year,publicationTypes,publicationVenue,referenceCount,citationCount,url,fieldsOfStudy,authors"
    NO_NESTED_FIELDS = "paperId,title,abstract,publicationTypes,referenceCount,citationCount,url,fieldsOfStudy,embedding,tldr,openAccessPdf,publicationDate"
    FULL_PAPER_FIELDS = "paperId,title,abstract,publicationTypes,publicationVenue,referenceCount,citationCount,url,fieldsOfStudy,authors,embedding,tldr,openAccessPdf,publicationDate,references"

    author_service = AuthorService()
    publicationVenueService = PublicationVenueService()

    def get_paper_by_id(self, id):
        try:
            paper = self.queryset.get(paperId=id)
            # if paper exists in database but not in full form
            if paper.publicationDate is None:
                paper = self.get_external_paper_by_id(
                    id, including_nested_fields=True
                )  # fetch full data and update database
                paper.save()
        except Paper.DoesNotExist:
            try:
                paper = self.get_external_paper_by_id(id)
                paper.save()
            except SemanticAPIException:
                return None
        return paper

    def assign_data_to_paper(self, paper, paper_data, including_nested_fields):
        paper.url = paper_data["url"]
        paper.title = paper_data["title"]
        paper.abstract = paper_data["abstract"] if paper_data["abstract"] is not None else ""
        paper.referenceCount = paper_data["referenceCount"]
        paper.citationCount = paper_data["citationCount"]
        paper.openAccessPdf = (
            paper_data["openAccessPdf"]["url"] if paper_data["openAccessPdf"] is not None else ""
        )
        paper.embedding = (
            paper_data["embedding"]["vector"] if paper_data["embedding"] is not None else []
        )
        paper.tldr = paper_data["tldr"]["text"] if paper_data["tldr"] is not None else ""
        paper.publicationDate = paper_data["publicationDate"]
        paper.publicationTypes = (
            paper_data["publicationTypes"] if paper_data["publicationTypes"] is not None else []
        )
        paper.fieldsOfStudy = (
            paper_data.get("fieldsOfStudy") if paper_data.get("fieldsOfStudy") else []
        )

        if including_nested_fields:
            # references authors and publicationVenue
            references_data = list(
                filter(lambda ref: ref["paperId"] is not None, paper_data.get("references", []))
            )
            authors_data = list(
                filter(
                    lambda author: author["authorId"] is not None, paper_data.get("authors", [])
                )
            )

            # add references
            references_ids = [ref["paperId"] for ref in references_data]
            existing_references = self.queryset.filter(paperId__in=references_ids)
            existing_reference_ids = set([ref.paperId for ref in existing_references])
            new_references = self.queryset.bulk_create(
                [
                    Paper(paperId=ref["paperId"], title=ref["title"])
                    for ref in references_data
                    if ref["paperId"] not in existing_reference_ids
                ]
            )

            # add authors
            authors_ids = [author["authorId"] for author in authors_data]
            existing_authors = self.author_service.queryset.filter(authorId__in=authors_ids)
            existing_author_ids = set([author.authorId for author in existing_authors])
            new_authors = self.author_service.queryset.bulk_create(
                [
                    Author(authorId=author["authorId"], name=author["name"])
                    for author in authors_data
                    if author["authorId"] not in existing_author_ids
                ]
            )

            # Add references and authors to paper
            paper.references.add(*existing_references, *new_references)
            paper.authors.add(*existing_authors, *new_authors)

            # Add publicationVenue to paper
            publicationVenue_data = paper_data["publicationVenue"]
            if publicationVenue_data is not None and "id" in publicationVenue_data:
                publicationVenue = self.publicationVenueService.get_publicationVenue_or_create(
                    publicationVenue_data
                )
                paper.publicationVenue = publicationVenue

        return paper

    def get_external_paper_by_id(self, id, including_nested_fields=True):
        if including_nested_fields:
            response = requests.get(
                os.path.join(self.BASE_URL, id), params={"fields": self.FULL_PAPER_FIELDS}
            )
        else:
            response = requests.get(
                os.path.join(self.BASE_URL, id), params={"fields": self.NO_NESTED_FIELDS}
            )

        if response.status_code != 200:
            # You might want to add more specific error handling here
            raise SemanticAPIException(f"Semantic API returned status code {response.status_code}")

        paper_data = response.json()
        paper = self.queryset.get_or_create(
            paperId=paper_data["paperId"],
        )[0]
        return self.assign_data_to_paper(paper, paper_data, including_nested_fields)

    def save_external_paper_by_id(self, id, including_nested_fields=True):
        paper = self.get_external_paper_by_id(id, including_nested_fields)
        paper.save()

    def get_external_papers_by_ids(self, ids, including_nested_fields=True):
        if including_nested_fields:
            params = {"fields": self.FULL_PAPER_FIELDS}
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
            # You might want to add more specific error handling here
            raise SemanticAPIException(f"Semantic API returned status code {response.status_code}")

        papers_data = response.json()
        papers = []
        for paper_data in papers_data:
            paper = self.queryset.get_or_create(
                paperId=paper_data["paperId"],
            )[0]
            self.assign_data_to_paper(paper, paper_data, including_nested_fields)
            papers.append(paper)
        return papers

    def save_external_papers_by_ids(self, ids, including_nested_fields=True):
        papers = self.get_external_papers_by_ids(ids, including_nested_fields)
        self.queryset.bulk_update(
            papers,
            fields=[
                "url",
                "title",
                "abstract",
                "referenceCount",
                "citationCount",
                "openAccessPdf",
                "embedding",
                "tldr",
                "publicationDate",
                "publicationTypes",
                "fieldsOfStudy",
            ],
        )

    def search_external_papers(self, query, page=1):
        params = {
            "query": query,
            "limit": self.RECORDS_PER_PAGE,
            "offset": (page - 1) * self.RECORDS_PER_PAGE,
            "fields": self.BASIC_PAPER_FIELDS,
        }
        response = requests.get(os.path.join(self.BASE_URL, "search"), params=params)
        data = response.json()
        return data

    def get_papers_by_topic(self, topic, num=30, including_nested_fields=True):
        if including_nested_fields:
            fields = self.FULL_PAPER_FIELDS
        else:
            fields = self.NO_NESTED_FIELDS
        response = requests.get(
            os.path.join(self.BASE_URL, "search"),
            params={"query": topic, "limit": num, "fields": fields},
        )
        return response.json()["data"]

    def autocomplete(self, query):
        return requests.get(
            os.path.join(self.BASE_URL, "autocomplete"), params={"query": query}
        ).json()

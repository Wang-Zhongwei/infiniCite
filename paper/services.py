import os

import requests
from author.models import Author
from author.services import AuthorService, PublicationVenueService

from paper.exceptions import SemanticAPIException
from paper.models import Library, Paper


class PaperService:
    BASE_URL = "http://api.semanticscholar.org/graph/v1/paper"
    queryset = Paper.objects.all()
    RECORDS_PER_PAGE = 10
    BASIC_PAPER_FIELDS = "paperId,title,abstract,year,publicationTypes,publicationVenue,referenceCount,citationCount,url,fieldsOfStudy,authors"
    FULL_PAPER_FIELDS = "paperId,title,abstract,year,publicationTypes,publicationVenue,referenceCount,citationCount,url,fieldsOfStudy,authors,embedding,tldr,openAccessPdf,publicationDate,references"

    author_service = AuthorService()
    publicationVenueService = PublicationVenueService()

    def get_paper_by_id(self, id):
        try:
            paper = self.queryset.get(paperId=id)
            # if paper exists in database but not in full form
            if paper.referenceCount is None:
                paper = self.get_external_paper_by_id(
                    id, should_save=True
                )  # fetch full data and update database
        except Paper.DoesNotExist:
            try:
                paper = self.get_external_paper_by_id(id)
            except SemanticAPIException:
                return None
        return paper

    def get_external_paper_by_id(self, id, should_save=True):
        response = requests.get(
            os.path.join(self.BASE_URL, id), params={"fields": self.FULL_PAPER_FIELDS}
        )

        if response.status_code != 200:
            # You might want to add more specific error handling here
            raise SemanticAPIException(f"Semantic API returned status code {response.status_code}")

        paper_data = response.json()
        paper = self.queryset.update_or_create(
            paperId=paper_data["paperId"],
            url=paper_data["url"],
            title=paper_data["title"],
            abstract=paper_data["abstract"] if paper_data["abstract"] is not None else "",
            referenceCount=paper_data["referenceCount"],
            citationCount=paper_data["citationCount"],
            openAccessPdf=paper_data["openAccessPdf"]["url"]
            if paper_data["openAccessPdf"] is not None
            else "",
            embedding=paper_data["embedding"]["vector"]
            if paper_data["embedding"] is not None
            else [],
            tldr=paper_data["tldr"]["text"] if paper_data["tldr"] is not None else "",
            publicationDate=paper_data["publicationDate"],
            publicationTypes=paper_data["publicationTypes"]
            if paper_data["publicationTypes"] is not None
            else [],
            fieldsOfStudy=paper_data["fieldsOfStudy"],
        )[0]
        if should_save:
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
            if publicationVenue is not None and "id" in publicationVenue:
                publicationVenue = self.publicationVenueService.get_publicationVenue_or_create(
                    publicationVenue_data
                )
                paper.publicationVenue = publicationVenue

            paper.save()
        return paper

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

    def autocomplete(self, query):
        return requests.get(
            os.path.join(self.BASE_URL, "autocomplete"), params={"query": query}
        ).json()

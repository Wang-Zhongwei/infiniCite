from typing import Any, Optional
from django.core.management.base import BaseCommand
from author.models import Author

from paper.exceptions import SemanticAPIException
from author.services import AuthorService


class Command(BaseCommand):
    help = "Populate non-complete items from API. Including nested fields is equivalent one-step BFS traversal."
    author_service = AuthorService()
    
    def handle(self, *args: Any, **options: Any) -> str | None:
        incomplete_authors = Author.objects.filter(citationCount__isnull=True).values("authorId", "name")
        for author in incomplete_authors:
            try:
                author = self.author_service.get_external_author_by_id(author["authorId"])
                author.save()
                self.stdout.write(f"Successfully updated author {author['name']}")
            except SemanticAPIException:
                self.stdout.write(f"Failed to update author {author['name']}")

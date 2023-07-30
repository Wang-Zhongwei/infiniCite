import time
from typing import Any, Optional
from django.core.management.base import BaseCommand
from author.models import Author

from paper.exceptions import SemanticAPIException
from author.services import AuthorService


class Command(BaseCommand):
    help = "Populate non-complete items from API. Including nested fields is equivalent one-step BFS traversal."
    author_service = AuthorService()

    def add_arguments(self, parser):
        parser.add_argument(
            "--batch_size",
            type=int,
            default=32,
            help="Number of papers to update at a time. Default is 16.",
        )
        parser.add_argument(
            "--including_nested_fields",
            action="store_true",
            default=False,
            help="Whether to include nested fields. Default is False.",
        )

    def handle(self, *args: Any, **kwargs: Any) -> str | None:
        including_nested_fields = kwargs.get("including_nested_fields", False)
        batch_size = kwargs.get("batch_size", None)

        if including_nested_fields:
            incomplete_authors = Author.objects.filter(papers__isnull=True).values_list(
                "authorId", flat=True
            )
        else:
            incomplete_authors = Author.objects.filter(citationCount__isnull=True).values_list(
                "authorId", flat=True
            )

        print(f"Found {len(incomplete_authors)} incomplete authors")

        time_to_sleep = 0.5
        for i in range(0, len(incomplete_authors), batch_size):
            author_ids = incomplete_authors[i : i + batch_size]
            while True:
                try:
                    self.author_service.save_external_authors_by_ids(
                        author_ids, including_nested_fields
                    )
                    print(f"Successfully updated {len(author_ids)} authors")
                    time_to_sleep = 0.5
                    break
                except SemanticAPIException as e:
                    print(f"Failed to update {len(author_ids)} authors due to {e}.")
                    if e.status_code == 429:
                        print(f"Sleeping for {time_to_sleep} seconds")
                        time.sleep(time_to_sleep)
                        time_to_sleep *= 2
                        continue
                    else:
                        break

import time
from django.core.management.base import BaseCommand
from paper.exceptions import SemanticAPIException
from paper.services import PaperService


class Command(BaseCommand):
    help = "Populate non-complete items from API. Including nested fields is equivalent one-step BFS traversal."
    paper_service = PaperService()

    def add_arguments(self, parser):
        parser.add_argument(
            "--including_nested_fields",
            action="store_true",
            default=False,
            help="Whether to save references. Default is False.",
        )
        parser.add_argument(
            "--batch_size",
            type=int,
            help="Number of papers to update at a time. Default is 16.",
        )

    def handle(self, *args, **kwargs):
        # Query all incomplete items. Replace with your actual check for completeness
        including_nested_fields = kwargs["including_nested_fields"]
        batch_size = kwargs.get("batch_size", None)
        if batch_size is None:
            if including_nested_fields:
                batch_size = 16
            else:
                batch_size = 64

        if including_nested_fields:
            incomplete_items_ids = self.paper_service.queryset.filter(references__isnull=True).values_list(
                "paperId", flat=True
            )
        else:
            incomplete_items_ids = self.paper_service.queryset.filter(publicationDate__isnull=True).values_list(
                "paperId", flat=True
            )
        print(f'Found {len(incomplete_items_ids)} incomplete papers')
        time_to_sleep = 0.5
        for i in range(0, len(incomplete_items_ids), batch_size):
            paper_ids = incomplete_items_ids[i : i + batch_size]
            while True:
                try:
                    self.paper_service.save_external_papers_by_ids(
                        paper_ids, including_nested_fields
                    )
                    print(f"Successfully updated {len(paper_ids)} papers")
                    time_to_sleep = 0.5
                    break
                except SemanticAPIException as e:
                    print(f"Failed to update {len(paper_ids)} papers due to {e}.")
                    if e.status_code == 429:
                        print(f"Sleeping for {time_to_sleep} seconds")
                        time.sleep(time_to_sleep)
                        time_to_sleep *= 2
                        continue
                    else:
                        break

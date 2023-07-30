from django.core.management.base import BaseCommand
import paper
from paper.exceptions import SemanticAPIException
from paper.services import AuthorService
from paper.models import Paper


class Command(BaseCommand):
    help = "Populate non-complete items from API. Including nested fields is equivalent one-step BFS traversal."
    paper_service = AuthorService()

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
            default=16,
            help="Number of papers to update at a time. Default is 16.",
        )

    def handle(self, *args, **kwargs):
        # Query all incomplete items. Replace with your actual check for completeness
        including_nested_fields = kwargs["including_nested_fields"]
        batch_size = kwargs["batch_size"]

        if including_nested_fields:
            incomplete_items_ids = Paper.objects.filter(references__isnull=True).values_list("paperId", flat=True)
        else:
            incomplete_items_ids = Paper.objects.filter(publicationDate__isnull=True).values_list("paperId", flat=True)

        for i in range(0, len(incomplete_items_ids), batch_size):
            paper_ids = incomplete_items_ids[i:i+batch_size]
            try:
                self.paper_service.save_external_papers_by_ids(paper_ids, including_nested_fields)
                print(f"Successfully updated {len(paper_ids)} papers")
            except SemanticAPIException:
                print(f"Failed to update {len(paper_ids)} papers")
                continue 

        paper_ids = incomplete_items_ids[len(incomplete_items_ids) - len(incomplete_items_ids) % batch_size:]
        try:
            self.paper_service.save_external_papers_by_ids(paper_ids, including_nested_fields)
            print(f"Successfully updated {len(paper_ids)} papers")
        except SemanticAPIException:
            print(f"Failed to update {len(paper_ids)} papers")
        

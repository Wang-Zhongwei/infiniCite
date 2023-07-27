from django.core.management.base import BaseCommand
from django.conf import settings

from paper.exceptions import SemanticAPIException
from paper.services import PaperService
from paper.models import Paper
import time


class Command(BaseCommand):
    help = "Populate non-complete items from API"
    paper_service = PaperService()

    def add_arguments(self, parser):
        parser.add_argument(
            "--including_nested_fields",
            action="store_true",
            default=False,
            help="Whether to save references",
        )

    def handle(self, *args, **kwargs):
        # Query all incomplete items. Replace with your actual check for completeness
        including_nested_fields = kwargs["including_nested_fields"]
        incomplete_items = Paper.objects.filter(publicationDate__isnull=True)

        papers_to_save = []
        for item in incomplete_items:
            try:
                paper = self.paper_service.get_external_paper_by_id(
                    item.paperId, including_nested_fields
                )
                papers_to_save.append(paper)
                print(f"Updated {item.title}")
            except SemanticAPIException:
                print(f"Failed to update {item.title}")
                continue
            time.sleep(0.5)

        Paper.objects.bulk_create(papers_to_save)

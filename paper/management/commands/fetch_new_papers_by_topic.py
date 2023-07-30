from django.core.management.base import BaseCommand
from paper.models import Paper
from paper.services import PaperService


class Command(BaseCommand):
    help = "Fetch papers by topic"
    paperService = PaperService()

    def add_arguments(self, parser):
        parser.add_argument("topic", type=str, help="The topic to fetch papers for")
        parser.add_argument("--num", type=int, default=10, help="The number of papers to fetch")
        parser.add_argument(
            "--including_nested_fields",
            action="store_true",
            default=True,
            help="Whether to save references",
        )

    def handle(self, *args, **kwargs):
        topic = kwargs["topic"]
        num = kwargs["num"]
        including_nested_fields = kwargs["including_nested_fields"]

        # Fetch data from API. You may need to adjust the URL and parameters to match your actual API
        papers = self.paperService.get_papers_by_topic(topic, num, including_nested_fields)
        for paper_data in papers:
            paper, created = Paper.objects.get_or_create(paperId=paper_data["paperId"])
            if created:
                paper = self.paperService.assign_data_to_paper(
                    paper, paper_data, including_nested_fields
                )
                paper.save()
                self.stdout.write(f"Successfully created paper {paper.title}")
            else:
                self.stdout.write(f"Paper {paper.title} already exists, skipped")

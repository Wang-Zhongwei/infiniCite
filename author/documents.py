from django_elasticsearch_dsl import Document, fields
from paper.models import Paper
from .models import Author
from django_elasticsearch_dsl.registries import registry

# TODO: index author-index 
@registry.register_document
class AuthorDocument(Document):
    affiliations = fields.ListField(fields.TextField())
    externalIds = fields.ListField(fields.TextField())
    papers = fields.NestedField(
        properties={
            "paperId": fields.KeywordField(),
            "title": fields.TextField(),
        }
    )
    name = fields.TextField(
        fields={
            "keyword": fields.KeywordField(),
            "suggest": fields.CompletionField()
        }
    )

    class Index:
        name = "author-index"
    
    class Django:
        model = Author
        fields = [
            "paperCount",
            "citationCount",
            "hIndex",
        ]
        related_models = [Paper]
    
    def get_queryset(self):
        """Not mandatory but to improve performance we can select related in one sql request"""
        return (
            super(AuthorDocument, self)
            .get_queryset()
            .prefetch_related("papers")
        )
    
    def prepare_papers(self, instance):
        return [{"paperId": paper.paperId, "title": paper.title} for paper in instance.papers.all()]
    
    def get_instances_from_related(self, related_instance):
        """If related_models is set, define how to retrieve the Paper instance(s) from the related model."""
        if isinstance(related_instance, Paper):
            return related_instance.authors.all()

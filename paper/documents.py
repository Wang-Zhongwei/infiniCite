from django_elasticsearch_dsl import Document, fields
from .models import Library, Paper
from author.models import Author, PublicationVenue
from django_elasticsearch_dsl.registries import registry

@registry.register_document
class PaperDocument(Document):
    authors = fields.NestedField(properties={
        'authorId': fields.TextField(),
        'name': fields.TextField(),
        'affiliations': fields.TextField(),
        'paperCount': fields.IntegerField(),
        'citationCount': fields.IntegerField(),
        'hIndex': fields.IntegerField(),
    })

    publicationVenue = fields.NestedField(properties={
        'name': fields.TextField(),
        'type': fields.TextField(),
        'url': fields.TextField(),
        'alternate_names': fields.TextField(),
    })

    libraries = fields.NestedField(properties={
        'id': fields.TextField(),
        'name': fields.TextField(),
    })

    fieldsOfStudy = fields.ListField(fields.TextField())
    embedding = fields.ListField(fields.FloatField())
    publicationTypes = fields.ListField(fields.TextField())

    class Index:
        name = 'paper-index'

    class Django:
        model = Paper
        fields = [
            'paperId',
            'url',
            'title',
            'abstract',
            'referenceCount',
            'citationCount',
            'openAccessPdf',
            'tldr',
            'publicationDate',
        ]
        related_models = [Author, PublicationVenue, Library]

    def get_queryset(self):
        """Not mandatory but to improve performance we can select related in one sql request"""
        return super(PaperDocument, self).get_queryset().prefetch_related(
        'authors',
        'publicationVenue',
        'libraries'
    )

    # this is optional but allows you to perform custom indexing
    def prepare_libraries(self, instance):
        return [{'id': library.id, 'name': library.name} for library in instance.libraries.all()]

    def get_instances_from_related(self, related_instance):
        """If related_models is set, define how to retrieve the Paper instance(s) from the related model."""
        if isinstance(related_instance, Author):
            return related_instance.papers.all()
        elif isinstance(related_instance, PublicationVenue):
            return related_instance.papers.all()
        elif isinstance(related_instance, Library):
            return related_instance.papers.all()
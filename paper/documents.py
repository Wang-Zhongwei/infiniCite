from django_elasticsearch_dsl import Document, fields, DEDField
from .models import Library, Paper
from author.models import Author, PublicationVenue
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import Field


class DenseVectorField(DEDField, Field):
    name = "dense_vector"

    def __init__(self, attr=None, **kwargs):
        dims = 768
        index = True
        similarity = "l2_norm"
        super(DenseVectorField, self).__init__(
            attr=attr, dims=dims, index=index, similarity=similarity, **kwargs
        )


class RankFeatureField(DEDField, Field):
    name = "rank_features"

    def __init__(self, attr=None, **kwargs):
        positive_score_impact = True
        super(RankFeatureField, self).__init__(
            attr=attr, positive_score_impact=positive_score_impact, **kwargs
        )


@registry.register_document
class PaperDocument(Document):
    # ml = fields.NestedField(
    #     attr="ml",
    #     properties={
    #         "token": RankFeatureField(),
    #     },
    # )

    authors = fields.NestedField(
        properties={
            "authorId": fields.KeywordField(),
            "name": fields.TextField(fields={"keyword": fields.KeywordField()}),
        }
    )

    publicationVenue = fields.NestedField(
        properties={
            "id": fields.KeywordField(),
            "name": fields.TextField(fields={"keyword": fields.KeywordField()}),
            "type": fields.TextField(),
            "url": fields.TextField(),
            "alternate_names": fields.TextField(),
        }
    )

    libraries = fields.NestedField(
        properties={
            "id": fields.KeywordField(),
            "name": fields.TextField(),
        }
    )

    references = fields.NestedField(
        properties={
            "paperId": fields.KeywordField(),
            "title": fields.TextField(),
        }
    )

    citations = fields.NestedField(
        properties={
            "paperId": fields.KeywordField(),
            "title": fields.TextField(),
        }
    )

    fieldsOfStudy = fields.ListField(fields.TextField())
    embedding = DenseVectorField(attr="embedding")
    publicationTypes = fields.ListField(fields.TextField())
    publicationDate = fields.DateField()
    title = fields.TextField(
        fields={
            "keyword": fields.KeywordField(),
            "suggest": fields.CompletionField(),
        }
    )

    class Index:
        name = "paper-index"

    class Django:
        model = Paper
        fields = [
            "url",
            "abstract",
            "referenceCount",
            "citationCount",
            "openAccessPdf",
            "tldr",
        ]
        related_models = [Author, PublicationVenue, Library]

    def get_queryset(self):
        """Not mandatory but to improve performance we can select related in one sql request"""
        return (
            super(PaperDocument, self)
            .get_queryset()
            .prefetch_related("authors", "publicationVenue", "libraries")
        )

    # this is optional but allows you to perform custom indexing
    def prepare_libraries(self, instance):
        return [{"id": library.id, "name": library.name} for library in instance.libraries.all()]

    def prepare(self, instance):
        data = super().prepare(instance)
        return data

    def get_instances_from_related(self, related_instance):
        """If related_models is set, define how to retrieve the Paper instance(s) from the related model."""
        if isinstance(related_instance, Author):
            return related_instance.papers.all()
        elif isinstance(related_instance, PublicationVenue):
            return related_instance.papers.all()
        elif isinstance(related_instance, Library):
            return related_instance.papers.all()

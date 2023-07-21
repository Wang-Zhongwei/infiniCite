from django.db import models
from django.contrib.postgres.fields import ArrayField
from author.models import Author, PublicationVenue
from user.models import Account


class Paper(models.Model):
    paperId= models.CharField(max_length=255, primary_key=True)
    url = models.URLField(blank=True, null=True)
    title = models.CharField(max_length=255)
    abstract = models.TextField(blank=True, null=True)
    fieldsOfStudy = ArrayField(models.CharField(max_length=255), blank=True, default=list)
    referenceCount = models.IntegerField(null=True)
    citationCount = models.IntegerField(null=True)
    openAccessPdf = models.URLField(blank=True, null=True)
    embedding = ArrayField(models.FloatField(), blank=True, null=True)
    tldr = models.TextField(blank=True, null=True)
    publicationDate = models.DateField(blank=True, null=True)
    authors = models.ManyToManyField(Author, related_name='papers', blank=True, default=list)
    publicationVenue = models.ForeignKey(PublicationVenue, related_name='papers', blank=True, on_delete=models.CASCADE, null=True)
    publicationTypes = ArrayField(models.CharField(max_length=255), blank=True, default=list)
    references = models.ManyToManyField('self', related_name='citations', symmetrical=False, blank=True, default=list)

# TODO: add date created field
# TODO: add user permissions field: view, edit, full control
class Library(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='libraries')
    papers = models.ManyToManyField(Paper, related_name='libraries', blank=True, default=list)
    sharedWith = models.ManyToManyField(Account, related_name='sharedLibraries', blank=True, default=list)

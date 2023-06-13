from django.db import models
from django.contrib.postgres.fields import ArrayField
from author.models import Author
from user.models import Account

class Paper(models.Model):
    paperId= models.CharField(max_length=255, primary_key=True)
    url = models.URLField(blank=True)
    title = models.CharField(max_length=255)
    abstract = models.TextField(blank=True)
    referenceCount = models.IntegerField()
    citationCount = models.IntegerField()
    openAccessPdf = models.URLField(blank=True)
    embedding = ArrayField(models.FloatField(), blank=True)
    tldr = models.TextField(blank=True)
    publicationDate = models.DateField()
    authors = models.ManyToManyField(Author, related_name='papers', blank=True)

class Library(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='libraries')
    papers = models.ManyToManyField(Paper, related_name='libraries', blank=True)
    sharedWith = models.ManyToManyField(Account, related_name='sharedLibraries', blank=True)

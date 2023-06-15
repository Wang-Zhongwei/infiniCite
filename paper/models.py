from django.db import models
from django.contrib.postgres.fields import ArrayField
from author.models import Author
from user.models import Account

class Paper(models.Model):
    paperId= models.CharField(max_length=255, primary_key=True)
    url = models.URLField(blank=True)
    title = models.CharField(max_length=255)
    abstract = models.TextField(blank=True, default='')
    referenceCount = models.IntegerField()
    citationCount = models.IntegerField()
    openAccessPdf = models.URLField(blank=True, default='')
    embedding = ArrayField(models.FloatField(), blank=True, default=list)
    tldr = models.TextField(blank=True, default='')
    publicationDate = models.DateField()
    authors = models.ManyToManyField(Author, related_name='papers', blank=True)

class Library(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='libraries')
    papers = models.ManyToManyField(Paper, related_name='libraries', blank=True, default=list)
    sharedWith = models.ManyToManyField(Account, related_name='sharedLibraries', blank=True, default=list)

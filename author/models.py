from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.
class Author(models.Model):
    authorId = models.CharField(max_length=255, primary_key=True)
    externalIds = ArrayField(models.CharField(max_length=255), blank=True, default=list)
    name = models.CharField(max_length=255)
    affiliations = ArrayField(models.CharField(max_length=255), blank=True, default=list)
    paperCount = models.IntegerField(blank=True, null=True)
    citationCount = models.IntegerField(blank=True, null=True)
    hIndex = models.IntegerField(blank=True, null=True)

class PublicationVenue(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, null=True)
    url = models.URLField(blank=True, null=True)
    alternate_names = ArrayField(models.CharField(max_length=255), blank=True, default=list)
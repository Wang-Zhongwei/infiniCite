from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.
class Author(models.Model):
    authorId = models.CharField(max_length=255, primary_key=True)
    externalIds = ArrayField(models.CharField(max_length=255), blank=True, default=list)
    name= models.CharField(max_length=255)
    affiliations = ArrayField(models.CharField(max_length=255), blank=True, default=list)
    paperCount = models.IntegerField()
    citationCount = models.IntegerField()
    hIndex = models.IntegerField()

class PublicationVenue(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    url = models.URLField(blank=True)
    alternate_names = ArrayField(models.CharField(max_length=255), blank=True, default=list)
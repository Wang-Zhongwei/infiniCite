from django.db import models
from django.conf import settings

class Paper(models.Model):
    users_saved = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='papers_saved', blank=True)
    title = models.CharField(max_length=200)
    url = models.URLField()
    abstract = models.TextField()

from django.db import models
from django.contrib.auth.models import User

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    affiliation = models.CharField(max_length=255, blank=True, default='')
    picture = models.ImageField(null=True, blank=True, upload_to='media', default='default.jpg')

class SearchRecord(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, blank=False)
    query = models.TextField(blank=False, null=False)
    timestamp = models.DateTimeField(auto_now_add=True)


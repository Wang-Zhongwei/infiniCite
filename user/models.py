from django.db import models
from django.contrib.auth.models import User
from PIL import Image

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    affiliation = models.CharField(max_length=255, blank=True, default='')
    picture = models.ImageField(null=True, blank=True, upload_to='media')

class SearchRecord(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, blank=False)
    query = models.TextField(blank=False, null=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
       
    
def __str__(self):
    return f'Profile for user {self.user.username}'


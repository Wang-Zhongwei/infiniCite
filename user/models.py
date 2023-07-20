from django.db import models
from django.contrib.auth.models import User
from PIL import Image

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    field = models.CharField()
    picture = models.ImageField(null=True, blank=True, upload_to='media')
       
    
def __str__(self):
    return f'Profile for user {self.user.username}'


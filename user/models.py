from django.db import models
from django.contrib.auth.models import User

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    field_of_study = models.CharField()

def __str__(self):
    return f'Account for user {self.user.username}'

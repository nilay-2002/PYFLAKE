from django.db import models

# Create your models here.
class User(models.Model):
    Name = models.CharField(max_length=20)
    email = models.EmailField(max_length=20)
    account = models.CharField(max_length=50)
    username = models.CharField(max_length=20)
    baseURL = models.CharField(max_length=50)
    password = models.CharField(max_length=20)
    
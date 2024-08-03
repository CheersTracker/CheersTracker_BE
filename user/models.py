from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    username = models.CharField(max_length=50, unique=True)
    nickname = models.CharField(max_length=30, unique=True)
    gender = models.CharField(max_length=10)
    birthdate = models.DateField()

    def __str__(self):
        return self.username

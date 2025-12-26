# userauths/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser 

# Register your models here.

class User(AbstractUser ):
    email = models.EmailField(unique=True)
    bio = models.CharField(max_length=100, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] 

    def __str__(self):
        return self.username
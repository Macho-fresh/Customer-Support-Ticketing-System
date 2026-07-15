from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE = (
        ('Customer', 'Customer'),
        ('Agent', 'Agent')
            )
    role = models.CharField(max_length=20, choices=ROLE)

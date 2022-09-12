from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class SignUp(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    username = models.CharField(max_length=200, unique=True)
    email = models.EmailField(max_length=200)

    def __str__(self):
        return self.username

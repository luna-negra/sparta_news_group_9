from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class Accounts(AbstractUser):

    email = models.EmailField(unique=True,
                              blank=False,
                              null=False
                              )
    introduction = models.TextField(blank=True)
    r_token = models.CharField(max_length=300, default="")
    created = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField()

    class Meta:
        db_table: str = "Accounts"
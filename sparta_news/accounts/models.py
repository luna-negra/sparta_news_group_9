from django.db import models
from django.utils.dateformat import datetime
from django.contrib.auth.models import AbstractUser

# Create your models here.


# CONSTANT VARIABLES
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"



class Accounts(AbstractUser):

    username = models.CharField(unique=True,
                                max_length=30,
                                error_messages={
                                    "unique": "이미 등록된 계정명입니다.",
                                })
    email = models.EmailField(unique=True,
                              error_messages ={
                                "unique": "이미 등록된 이메일 주소입니다.",
                                }
                              )
    introduction = models.TextField(blank=True)
    r_token = models.CharField(max_length=300, default="")
    created = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(default=datetime.strptime("1970-01-01 00:00:00",
                                                                DATETIME_FORMAT), blank=True)

    class Meta:
        db_table: str = "Accounts"

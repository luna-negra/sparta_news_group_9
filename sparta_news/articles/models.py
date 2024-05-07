from django.db import models
from accounts.models import Accounts
# Create your models here.


class Articles(models.Model):
    user = models.ForeignKey(to=Accounts,
                            related_name="articles",
                            on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    url = models.URLField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table: str = "Articles"


class Comments(models.Model):
    user = models.ForeignKey(to=Accounts,
                            related_name="comments",
                            on_delete=models.CASCADE)
    article = models.ForeignKey(to=Articles,
                                related_name="comments",
                                on_delete=models.CASCADE)
    content = models.CharField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table: str = "Comments"
from django.urls import path
from .views import *


app_name: str = "articles"
urlpatterns: list = [
    path("", test),
]
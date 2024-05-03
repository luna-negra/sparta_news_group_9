from django.urls import path
from .views import *


app_name: str = "accounts"
urlpatterns: list = [
    path("", test),
]
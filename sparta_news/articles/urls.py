from django.urls import path
from . import views

app_name: str = "articles"
urlpatterns: list = [
    path("update/", views.ArticlesDetailAPIView.as_view(), name="update"),
    path("delete/", views.ArticlesDetailAPIView.as_view(), name="delete"),
]

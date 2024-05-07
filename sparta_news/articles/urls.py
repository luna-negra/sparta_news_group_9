from django.urls import path
from . import views

app_name: str = "articles"
urlpatterns: list = [
    path("<int:pk>/update/", views.ArticlesDetailAPIView.as_view(), name="update"),
    path("<int:pk>/delete/", views.ArticlesDetailAPIView.as_view(), name="delete"),
]

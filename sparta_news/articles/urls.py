from django.urls import path
from .views import *
from . import views


app_name: str = "articles"
urlpatterns: list = [
    path("", test),
    path("<int:article_id>/comments",views.CommentListCreatView.as_view()),
    path("comments/<int:comment_id>",views.CommentDetailView.as_view()),
]
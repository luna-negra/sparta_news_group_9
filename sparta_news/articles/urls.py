from django.urls import path
from .views import *
from . import views


app_name: str = "articles"
urlpatterns: list = [
    path("", test),
    path("comments/<int:article_id>",views.CommentListCreatView.as_view()),
    # path("comments/detail/<int:comment_id>",views.CommentDetailView.as_view()),
]
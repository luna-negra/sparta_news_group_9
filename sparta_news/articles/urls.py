from django.urls import path
from . import views


app_name: str = "articles"
urlpatterns: list = [

    path("", views.ArticleListView.as_view(), name="articles"),
    path("<int:article_pk>/", views.ArticlesDetailAPIView.as_view(), name="detail"),
    path("<int:article_pk>/", views.ArticlesDetailAPIView.as_view(), name="update"),
    path("<int:article_pk>/", views.ArticlesDetailAPIView.as_view(), name="delete"),
    path("<int:article_pk>/comments/",views.CommentListCreateAPIView.as_view()),
    path("comments/<int:comment_pk>/", views.CommentDetailAPIView.as_view()),
]

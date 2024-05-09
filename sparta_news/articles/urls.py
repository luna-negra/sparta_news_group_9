from django.urls import path
from . import views


app_name: str = "articles"
urlpatterns: list = [
    path("", views.ArticleListView.as_view(), name="articles"),
    path("search/", views.ArticlesSearchAPIView.as_view(), name="search"),
    path("<int:article_pk>/", views.ArticlesDetailAPIView.as_view(), name="detail"),
    path("<int:article_pk>/", views.ArticlesDetailAPIView.as_view(), name="update"),
    path("<int:article_pk>/", views.ArticlesDetailAPIView.as_view(), name="delete"),
    path("<int:article_pk>/comments/",views.CommentListCreateAPIView.as_view()),
    path("comments/<int:comment_pk>/", views.CommentDetailAPIView.as_view()),
    path("<int:article_pk>/scrap/", views.scrap_article),
    path("<int:article_pk>/unscrap/", views.unscrap_article),
    path("<int:article_pk>/email/", views.email_article)
]

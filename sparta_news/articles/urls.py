from django.urls import path
from .views import *
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)



app_name: str = "articles"
urlpatterns: list = [

    path("", views.ArticleListView.as_view(), name="articles"),
    path("<int:pk>/", views.ArticlesDetailAPIView.as_view(), name="detail"),
    path("<int:pk>/update/", views.ArticlesDetailAPIView.as_view(), name="update"),
    path("<int:pk>/delete/", views.ArticlesDetailAPIView.as_view(), name="delete"),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path("<int:article_id>/comments",views.CommentListCreatView.as_view()),

]
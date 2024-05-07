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
    path("<int:article_pk>/comments/",views.CommentListCreatAPIView.as_view()),
    path("comments/<int:comment_pk>/", views.CommentDetailAPIView.as_view()),

]

"""
urls.py 및 views.py 수정 제안 사항 (/api/articles/)

1. URL 정리
                
(1) URL : "<int:article_id>/"
*  view class:  ArticleDetailView(APIView)

DetailView를 사용하고 있기 때문에 URL 뒤에 상세 주소는 작성하지 않아도 괜찮습니다. 시연하면서 보여드릴게요!
그리고 Comments 쪽의 <int:>와 포맷을 맞추는 것이 추후에도 수정이 용이할 듯 합니다.

-  <int:pk>/update/   =>  <int:article_pk>
-  <intLpk>/delete/   =>  <int:article_pk>


(2) Comments URL Path '/' 누락 추가 요청

  :)
 
"""

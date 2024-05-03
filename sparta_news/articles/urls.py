from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


app_name: str = "articles"
urlpatterns: list = [
    path("", views.ArticleListView.as_view(), name="articles"),
    path("<int:pk>/", views.ArticleDetailView.as_view(), name="detail"),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
]
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from .import views


app_name: str = "accounts"
urlpatterns: list = [
    path("", views.SignupAPIView.as_view(), name="signup"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
]
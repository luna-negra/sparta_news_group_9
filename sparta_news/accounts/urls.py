from django.urls import path
from .views import *


app_name: str = "accounts"
urlpatterns: list = [
    path("signin/", AccountSignInView.as_view()),
    path("signup/", signup),
    path("signout/", signout),
    path("<int:account_id>/", AccountDetailView.as_view()),
]
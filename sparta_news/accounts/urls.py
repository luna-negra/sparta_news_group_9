from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import *

app_name: str = ""
urlpatterns: list = [
    path("signin/", AccountSignInView.as_view()),
    path("signup/", signup),
    path("signout/", signout),
    path("<int:account_id>/", AccountDetailView.as_view()),
]

from django.urls import path
from . import views

app_name: str = ""
urlpatterns: list = [
    path("signin/", AccountSignInView.as_view()),
    path("signup/", signup),
    path("signout/", signout),
    path("<int:account_id>/", AccountDetailView.as_view()),
]

from django.urls import path

from . import views

app_name = "getpaid_payu"

urlpatterns = [
    path(
        "callback/",
        views.CallbackView.as_view(),
        name="callback",
    ),
]

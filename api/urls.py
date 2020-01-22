from django.urls import path
from rest_framework.authtoken.views import ObtainAuthToken


urlpatterns = [
    path('v1/signin/', ObtainAuthToken.as_view()),
]

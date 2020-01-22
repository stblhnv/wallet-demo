from django.urls import path
from rest_framework.authtoken.views import ObtainAuthToken

from .views import UserRegistrationView


urlpatterns = [
    path('v1/signin/', ObtainAuthToken.as_view()),
    path('v1/signup/', UserRegistrationView.as_view()),
]

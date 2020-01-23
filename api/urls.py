from django.urls import path
from rest_framework.authtoken.views import ObtainAuthToken

from .views import (
    TransmitMoneyView,
    UserRegistrationView,
    UserTransactionsView,
)


urlpatterns = [
    path('v1/signin/', ObtainAuthToken.as_view()),
    path('v1/signup/', UserRegistrationView.as_view()),
    path('v1/transmit_money/', TransmitMoneyView.as_view()),
    path('v1/transactions/<int:wallet_id>/', UserTransactionsView.as_view()),
]

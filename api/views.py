from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_200_OK,
)
from rest_framework.views import APIView

from wallet.services import transfer_money_between_wallets
from .services import create_user_and_wallet
from .serializers import (
    MoneyTransferSerializer,
    UserRegistrationSerializer,
)


class UserRegistrationView(APIView):

    def post(self, request):
        input_serializer = UserRegistrationSerializer(data=request.data)
        try:
            if input_serializer.is_valid(raise_exception=True):
                create_user_and_wallet(
                    email=input_serializer.validated_data['email'],
                    password=input_serializer.validated_data['password1'],
                    currency=input_serializer.validated_data['currency'],
                    init_balance=input_serializer.validated_data['init_balance'],
                )
                return Response(
                    {
                        'message': 'User is successfully created',
                        'status': HTTP_201_CREATED,
                    },
                    status=HTTP_201_CREATED,
                )
        except Exception as error:
            return Response(
                {
                    'error': str(error),
                    'status': HTTP_400_BAD_REQUEST,
                },
                status=HTTP_400_BAD_REQUEST,
            )


class TransmitMoneyView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request):
        input_serializer = MoneyTransferSerializer(data=request.data)
        try:
            if input_serializer.is_valid(raise_exception=True):
                transaction = transfer_money_between_wallets(
                    sender=request.user,
                    sender_wallet_id=input_serializer.validated_data['sender'],
                    recipient_wallet_id=input_serializer.validated_data['recipient'],
                    amount=input_serializer.validated_data['amount'],
                )
                return Response(
                    {
                        'message': f'You successfully transmitted '
                                   f'{transaction.amount} {transaction.sender.currency} '
                                   f'to {transaction.recipient}',
                        'status': HTTP_200_OK,
                    },
                    status=HTTP_200_OK,
                )
        except Exception as error:
            return Response(
                {
                    'error': str(error),
                    'status': HTTP_400_BAD_REQUEST,
                },
                status=HTTP_400_BAD_REQUEST,
            )

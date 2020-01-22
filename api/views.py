from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
)
from rest_framework.views import APIView

from .services import create_user_and_wallet
from .serializers import UserRegistrationSerializer


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

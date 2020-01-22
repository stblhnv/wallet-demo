from rest_framework import serializers

from wallet.models import CURRENCY_TYPES


class UserRegistrationSerializer(serializers.Serializer):

    email = serializers.EmailField(
        required=True,
        help_text='Email',
    )
    password1 = serializers.CharField(
        required=True,
        max_length=50,
        help_text='Пароль',
    )
    password2 = serializers.CharField(
        required=True,
        max_length=50,
        help_text='Повторите пароль',
    )
    init_balance = serializers.DecimalField(
        required=True,
        max_digits=11,
        decimal_places=2,
        min_value=0,
        max_value=999999999,
        help_text='Начальный баланс кошелька',
    )
    currency = serializers.ChoiceField(
        required=True,
        choices=CURRENCY_TYPES,
        help_text='Валюта кошелька',
    )

    def validate_password1(self, password1: str):
        if password1 != self.initial_data['password2']:
            raise serializers.ValidationError('password1 and password2 are not equal')
        return password1

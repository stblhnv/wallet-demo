from rest_framework import serializers

from wallet.models import Transaction


class MoneyTransferSerializer(serializers.Serializer):

    sender = serializers.IntegerField(
        required=True,
    )
    recipient = serializers.IntegerField(
        required=True,
    )
    amount = serializers.DecimalField(
        required=True,
        min_value=0,
        max_value=999999999,
        max_digits=11,
        decimal_places=2,
    )


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = [
            'sender',
            'recipient',
            'amount',
            'exchange_rate',
            'created_at',
        ]

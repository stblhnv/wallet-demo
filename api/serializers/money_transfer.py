from rest_framework import serializers


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

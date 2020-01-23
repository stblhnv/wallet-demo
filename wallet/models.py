from decimal import Decimal

from django.conf import settings
from django.contrib.postgres import fields
from django.db import models


USD = 'USD'
EUR = 'EUR'
RUB = 'RUB'
GBP = 'GBP'
CURRENCIES = {
    USD,
    EUR,
    RUB,
    GBP,
}
CURRENCY_TYPES = (
    (USD, 'USD'),
    (EUR, 'EUR'),
    (RUB, 'RUB'),
    (GBP, 'GBP'),
)


class Wallet(models.Model):

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='wallets',
        verbose_name='Владелец кошелька',
        help_text='Владелец кошелька',
    )
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_TYPES,
        verbose_name='Валюта кошелька',
        help_text='Код валюты по ISO',
    )
    balance = models.DecimalField(
        max_digits=11,
        decimal_places=2,
        verbose_name='Баланс кошелька',
        help_text='Текущий баланс кошелька, ограничение в 1 млрд',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время создания кошелька',
        help_text='Дата и время создания кошелька',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен',
        help_text='Активен',
    )

    def __str__(self):
        return f'{self.owner}: #{self.pk}({self.currency})'


class ExchangeRate(models.Model):

    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_TYPES,
        verbose_name='Базовая валюта конвертирования',
        help_text='Код базовой валюты конвертирования по ISO',
    )
    rates = fields.JSONField(
        verbose_name='JSON с курсами валют',
        help_text='JSON с курсами валют',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время создания записи о курсах валют',
        help_text='Дата и время создания записи о курсах валют',
    )


class Transaction(models.Model):

    sender = models.ForeignKey(
        Wallet,
        on_delete=models.PROTECT,
        related_name='transactions_as_sender',
        verbose_name='Кошелёк отправителя',
        help_text='Кошелёк отправителя',
    )
    recipient = models.ForeignKey(
        Wallet,
        on_delete=models.PROTECT,
        related_name='transactions_as_recipient',
        verbose_name='Кошелёк получателя',
        help_text='Кошелёк получателя',
    )
    amount = models.DecimalField(
        max_digits=11,
        decimal_places=2,
        verbose_name='Сумма перевода',
        help_text='Ограничение в 1 млрд',
    )
    exchange_rate = models.DecimalField(
        max_digits=10,
        decimal_places=5,
        default=Decimal(1),
        verbose_name='Обменный курс на момент транзакции',
        help_text='Обменный курс на момент транзакции',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время создания записи о переводе',
        help_text='Дата и время создания записи о переводе',
    )

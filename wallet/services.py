from decimal import (
    Decimal,
    ROUND_HALF_DOWN,
)
from typing import Dict

from customauth.models import CustomUser
from .exceptions import (
    ExchangeRateCreationException,
    WalletCreationException,
)
from .models import (
    CURRENCIES,
    ExchangeRate,
    Wallet,
)
from .repositories.exchangeratesapi import get_exchange_rates


def create_exchange_rate(
        currency: str,
        exchange_rates: Dict[str, float],
) -> ExchangeRate:
    if currency in CURRENCIES and set(exchange_rates.keys()) - CURRENCIES == set():
        return ExchangeRate.objects.create(
            currency=currency,
            rates=exchange_rates,
        )
    raise ExchangeRateCreationException(
        f'Unknown currencies found among ({currency}, {exchange_rates}).',
    )


def update_exchange_rates() -> None:
    for currency in CURRENCIES:
        target_currencies = CURRENCIES - {currency}
        new_rates = get_exchange_rates(
            base_currency=currency,
            target_currencies=target_currencies,
        )
        create_exchange_rate(
            currency=currency,
            exchange_rates=new_rates,
        )


def create_wallet(
        user: CustomUser,
        currency: str,
        init_balance: Decimal,
) -> Wallet:
    if init_balance >= 0 and currency in CURRENCIES:
        cents = Decimal('.01')
        return Wallet.objects.create(
            owner=user,
            currency=currency,
            balance=Decimal(init_balance).quantize(cents, ROUND_HALF_DOWN),
        )
    raise WalletCreationException(
        'Unable to create wallet with negative balance or currency is unknown',
    )

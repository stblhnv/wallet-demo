from typing import Dict

from .exceptions import ExchangeRateCreationException
from .models import (
    CURRENCIES,
    ExchangeRate,
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

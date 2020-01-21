from typing import List, Dict

import requests

from .exceptions import ExchangeRatesApiException


EXCHANGE_RATES_URL = 'https://api.exchangeratesapi.io/latest'


def get_exchange_rates(
        base_currency: str,
        target_currencies: List[str],
) -> Dict[str, float]:

    target_url = EXCHANGE_RATES_URL
    params = {
        'base': base_currency,
        'symbols': target_currencies,
    }

    response = requests.get(
        url=target_url,
        params=params,
    )
    if response.status_code != 200:
        error = response.json()['error']
        raise ExchangeRatesApiException(error)

    return response.json()['rates']

import pytest
from unittest.mock import MagicMock

from wallet.repositories.exceptions import ExchangeRatesApiException
from wallet.repositories.exchangeratesapi import get_exchange_rates


def test_get_exchange_rates__proper_call__return_rates(mocker):
    # arrange
    response = mocker.patch(
        'wallet.repositories.exchangeratesapi.requests.get',
    )
    expected_data = {
        'rates': {
            'USD': 1.5,
            'RUB': 1,
            'EUR': 1.3,
        },
    }
    response.return_value = MagicMock(
        status_code=200,
        json=lambda: expected_data,
    )

    # act
    rates = get_exchange_rates(
        base_currency='RUB',
        target_currencies=['RUB', 'USD', 'EUR'],
    )

    # assert
    assert rates['USD'] == 1.5
    assert rates['RUB'] == 1
    assert rates['EUR'] == 1.3


def test_get_exchange_rates__wrong_currencies__raise_exception(mocker):
    # arrange
    response = mocker.patch(
        'wallet.repositories.exchangeratesapi.requests.get',
    )
    expected_data = {
        'error': 'Unknown currency RUM',
    }
    response.return_value = MagicMock(
        status_code=400,
        json=lambda: expected_data,
    )

    # act & assert
    with pytest.raises(ExchangeRatesApiException):
        get_exchange_rates(
            base_currency='RUM',
            target_currencies=['RUB', 'USD', 'EUR'],
        )

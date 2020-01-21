import pytest

from wallet.exceptions import ExchangeRateCreationException
from wallet.services import (
    create_exchange_rate,
    update_exchange_rates,
)


@pytest.mark.django_db
def test_create_exchange_rate__proper_call__return_exchange_rate():
    # act
    exchange_rate = create_exchange_rate(
        currency='USD',
        exchange_rates={'RUB': 1.2, 'GBP': 1.5, 'EUR': 1.1}
    )

    # assert
    assert exchange_rate.currency == 'USD'
    assert exchange_rate.rates['RUB'] == 1.2
    assert exchange_rate.rates['GBP'] == 1.5
    assert exchange_rate.rates['EUR'] == 1.1


@pytest.mark.django_db
def test_create_exchange_rate__unknown_currency__raise_exception():
    # act & assert
    with pytest.raises(ExchangeRateCreationException):
        create_exchange_rate(
            currency='RMB',
            exchange_rates={'RUB': 1.2, 'GBP': 1.5, 'EUR': 1.1}
        )


@pytest.mark.django_db
def test_update_exchange_rates__proper_call__called_4_times(mocker):
    # arrange
    create_exchange_rate_mocker = mocker.patch(
        'wallet.services.create_exchange_rate',
    )
    get_exchange_rates_mocker = mocker.patch(
        'wallet.services.get_exchange_rates',
    )

    # act
    update_exchange_rates()

    # assert
    assert create_exchange_rate_mocker.call_count == 4
    assert get_exchange_rates_mocker.call_count == 4

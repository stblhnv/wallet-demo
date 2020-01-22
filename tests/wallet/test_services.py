import pytest
from decimal import Decimal

from customauth.services import create_user
from wallet.exceptions import (
    ExchangeRateCreationException,
    WalletCreationException,
)
from wallet.services import (
    create_exchange_rate,
    create_wallet,
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


@pytest.mark.django_db
def test_create_wallet__proper_call__wallet_created():
    # arrange
    user = create_user(
        email='test@test.com',
        password='test',
    )

    # act
    wallet = create_wallet(
        user=user,
        currency='USD',
        init_balance=Decimal(1000.555),
    )

    # assert
    assert wallet.balance == Decimal('1000.55')
    assert wallet.owner is user
    assert wallet.currency == 'USD'


@pytest.mark.django_db
def test_create_wallet__wrong_currency__raise_exception():
    # arrange
    user = create_user(
        email='test@test.com',
        password='test',
    )

    # act & assert
    with pytest.raises(WalletCreationException):
        create_wallet(
            user=user,
            currency='SBM',
            init_balance=Decimal(1000.0),
        )


@pytest.mark.django_db
def test_create_wallet__negative_initial_balance__raise_exception():
    # arrange
    user = create_user(
        email='test@test.com',
        password='test',
    )

    # act & assert
    with pytest.raises(WalletCreationException):
        create_wallet(
            user=user,
            currency='USD',
            init_balance=Decimal(-10.0),
        )

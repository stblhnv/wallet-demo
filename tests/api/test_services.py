import pytest
from decimal import Decimal

from api.services import create_user_and_wallet
from customauth.services import create_user
from wallet.exceptions import WalletCreationException


@pytest.mark.django_db
def test_create_user_and_wallet__proper_call__user_and_wallet_created(mocker):
    # arrange
    email = 'test@test.com'
    password = 'password1'
    currency = 'RUB'
    init_balance = Decimal(100)
    user = create_user(
        email=email,
        password=password,
    )
    create_user_mocker = mocker.patch('api.services.create_user')
    create_user_mocker.return_value = user
    create_wallet_mocker = mocker.patch('api.services.create_wallet')

    # act
    create_user_and_wallet(
        email=email,
        password=password,
        currency=currency,
        init_balance=init_balance,
    )

    # assert
    assert create_user_mocker.called_once_with(
        email=email,
        password=password,
    )
    assert create_wallet_mocker.called_once_with(
        user=user,
        currency=currency,
        init_balance=init_balance,
    )


@pytest.mark.django_db
def test_create_user_and_wallet__unknown_currency__user_created(mocker):
    # arrange
    email = 'test@test.com'
    password = 'password1'
    currency = 'RMB'
    init_balance = Decimal(100)
    user = create_user(
        email=email,
        password=password,
    )
    create_user_mocker = mocker.patch('api.services.create_user')
    create_user_mocker.return_value = user
    create_wallet_mocker = mocker.patch('api.services.create_wallet')
    create_wallet_mocker.side_effect = WalletCreationException
    # act
    create_user_and_wallet(
        email=email,
        password=password,
        currency=currency,
        init_balance=init_balance,
    )

    # assert
    assert create_user_mocker.called_once_with(
        email=email,
        password=password,
    )
    assert create_wallet_mocker.called_once_with(
        user=user,
        currency=currency,
        init_balance=init_balance,
    )

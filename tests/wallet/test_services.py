import pytest
from decimal import Decimal

from customauth.services import create_user
from wallet.exceptions import (
    ExchangeRateCreationException,
    WalletCreationException,
    WalletOperationException,
)
from wallet.models import (
    ExchangeRate,
    Wallet,
)

from wallet.services import (
    convert_amount,
    create_exchange_rate,
    create_transaction,
    create_wallet,
    decrease_wallet_balance,
    get_current_exchange_rate,
    increase_wallet_balance,
    retrieve_transactions_by_wallet_id,
    transfer_money_between_wallets,
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


def test_convert_amount__proper_call__return_rate():
    # act
    new_amount = convert_amount(amount=Decimal(100.00), exchange_rate=Decimal(56.67651))

    # assert
    assert new_amount == Decimal('5667.65')


@pytest.mark.django_db
def test_decrease_wallet_balance__proper_call__decrease_balance_properly():
    # arrange
    user = create_user(
        email='test@test.com',
        password='test',
    )
    wallet = create_wallet(
        user=user,
        currency='USD',
        init_balance=Decimal(10.0),
    )

    # act
    decrease_wallet_balance(wallet=wallet, amount=Decimal(5.01))

    # assert
    assert wallet.balance == Decimal('4.99')


@pytest.mark.django_db
def test_decrease_wallet_balance__negative_amount__raise_exception():
    # arrange
    user = create_user(
        email='test@test.com',
        password='test',
    )
    wallet = create_wallet(
        user=user,
        currency='USD',
        init_balance=Decimal(10.0),
    )

    # act & assert
    with pytest.raises(WalletOperationException):
        decrease_wallet_balance(wallet=wallet, amount=Decimal(-5.01))


@pytest.mark.django_db
def test_decrease_wallet_balance__too_big_transfer__raise_exception():
    # arrange
    user = create_user(
        email='test@test.com',
        password='test',
    )
    wallet = create_wallet(
        user=user,
        currency='USD',
        init_balance=Decimal(10.0),
    )

    # act & assert
    with pytest.raises(WalletOperationException):
        decrease_wallet_balance(wallet=wallet, amount=Decimal(-95.01))


@pytest.mark.django_db
def test_increase_wallet_balance__proper_call__increase_balance_properly():
    # arrange
    user = create_user(
        email='test@test.com',
        password='test',
    )
    wallet = create_wallet(
        user=user,
        currency='USD',
        init_balance=Decimal(10.0),
    )

    # act
    increase_wallet_balance(wallet=wallet, amount=Decimal(5.01))

    # assert
    assert wallet.balance == Decimal('15.01')


@pytest.mark.django_db
def test_increase_wallet_balance__negative_amount__raise_exception():
    # arrange
    user = create_user(
        email='test@test.com',
        password='test',
    )
    wallet = create_wallet(
        user=user,
        currency='USD',
        init_balance=Decimal(10.0),
    )

    # act & assert
    with pytest.raises(WalletOperationException):
        increase_wallet_balance(wallet=wallet, amount=Decimal(-5.01))


@pytest.mark.django_db
def test_create_transaction__proper_call__return_transaction():
    # arrange
    user = create_user(
        email='test@test.com',
        password='test',
    )
    wallet_1 = create_wallet(
        user=user,
        currency='USD',
        init_balance=Decimal(50),
    )
    wallet_2 = create_wallet(
        user=user,
        currency='USD',
        init_balance=Decimal(0),
    )

    # act
    transaction = create_transaction(
        sender=wallet_1,
        recipient=wallet_2,
        amount=Decimal(40),
        exchange_rate=Decimal(1),
    )

    # assert
    assert transaction.exchange_rate == Decimal('1.00')
    assert transaction.sender is wallet_1
    assert transaction.recipient is wallet_2
    assert transaction.amount == Decimal('40.00')


@pytest.mark.django_db
def test_get_current_exchange_rate__proper_call__return_current_rates():
    # arrange
    create_exchange_rate(
        currency='RUB',
        exchange_rates={
            'USD': 63.5,
            'EUR': 73.1,
        },
    )

    # act
    current_exchange_rate = get_current_exchange_rate(
        base_currency='RUB',
        target_currency='USD',
    )

    # assert
    assert current_exchange_rate == Decimal('63.5')


@pytest.mark.django_db
def test_get_current_exchange_rate__unknown_currency__raise_exception():
    # act & assert
    with pytest.raises(ValueError):
        get_current_exchange_rate(
            base_currency='RMB',
            target_currency='USD',
        )


@pytest.mark.django_db
def test_get_current_exchange_rate__empty_query__raise_exception():
    # act & assert
    with pytest.raises(ExchangeRate.DoesNotExist):
        get_current_exchange_rate(
            base_currency='RUB',
            target_currency='USD',
        )


@pytest.mark.django_db
def test_transfer_money_between_wallets__proper_call__return_transaction(mocker):
    # arrange
    user_1 = create_user(
        email='test1@test.com',
        password='test1',
    )
    user_2 = create_user(
        email='test2@test.com',
        password='test2',
    )
    wallet_1 = create_wallet(
        user=user_1,
        currency='USD',
        init_balance=Decimal(50),
    )
    wallet_2 = create_wallet(
        user=user_2,
        currency='USD',
        init_balance=Decimal(0),
    )

    # act
    transaction = transfer_money_between_wallets(
        sender=user_1,
        sender_wallet_id=wallet_1.pk,
        recipient_wallet_id=wallet_2.pk,
        amount=Decimal(10.0),
    )
    wallet_1 = Wallet.objects.get(pk=wallet_1.pk)
    wallet_2 = Wallet.objects.get(pk=wallet_2.pk)

    # assert
    assert transaction.amount == Decimal('10.00')
    assert transaction.sender == wallet_1
    assert transaction.recipient == wallet_2
    assert transaction.exchange_rate == Decimal('1.0')
    assert wallet_1.balance == Decimal('40.00')
    assert wallet_2.balance == Decimal('10.00')


@pytest.mark.django_db
def test_transfer_money_between_wallets__wallet_does_not_exist__raise_exception(mocker):
    # arrange
    user_1 = create_user(
        email='test1@test.com',
        password='test1',
    )
    wallet_1 = create_wallet(
        user=user_1,
        currency='USD',
        init_balance=Decimal(50),
    )

    # act & assert
    with pytest.raises(Wallet.DoesNotExist):
        transfer_money_between_wallets(
            sender=user_1,
            sender_wallet_id=wallet_1.pk,
            recipient_wallet_id=100,
            amount=Decimal(10.0),
        )


@pytest.mark.django_db
def test_transfer_money_between_wallets__not_wallet_owner__raise_exception(mocker):
    # arrange
    user_1 = create_user(
        email='test1@test.com',
        password='test1',
    )
    user_2 = create_user(
        email='test2@test.com',
        password='test2',
    )
    wallet_1 = create_wallet(
        user=user_1,
        currency='USD',
        init_balance=Decimal(50),
    )
    wallet_2 = create_wallet(
        user=user_2,
        currency='USD',
        init_balance=Decimal(50),
    )

    # act & assert
    with pytest.raises(WalletOperationException):
        transfer_money_between_wallets(
            sender=user_1,
            sender_wallet_id=wallet_2.pk,
            recipient_wallet_id=wallet_1.pk,
            amount=Decimal(10.0),
        )


@pytest.mark.django_db
def test_transfer_money_between_wallets__multy_currency_transfer__return_transaction(mocker):
    # arrange
    user_1 = create_user(
        email='test1@test.com',
        password='test1',
    )
    user_2 = create_user(
        email='test2@test.com',
        password='test2',
    )
    wallet_1 = create_wallet(
        user=user_1,
        currency='USD',
        init_balance=Decimal(50),
    )
    wallet_2 = create_wallet(
        user=user_2,
        currency='RUB',
        init_balance=Decimal(0),
    )
    mocker.patch(
        'wallet.services.get_current_exchange_rate',
        return_value=Decimal('63.54563'),
    )

    # act
    transaction = transfer_money_between_wallets(
        sender=user_1,
        sender_wallet_id=wallet_1.pk,
        recipient_wallet_id=wallet_2.pk,
        amount=Decimal(10.0),
    )
    wallet_1 = Wallet.objects.get(pk=wallet_1.pk)
    wallet_2 = Wallet.objects.get(pk=wallet_2.pk)

    # assert
    assert transaction.amount == Decimal('10.00')
    assert transaction.sender == wallet_1
    assert transaction.recipient == wallet_2
    assert transaction.exchange_rate == Decimal('63.54563')
    assert wallet_1.balance == Decimal('40.00')
    assert wallet_2.balance == Decimal('635.46')


@pytest.mark.django_db
def test_transfer_money_between_wallets__unable_to_increase__raise_excpetion(mocker):
    # arrange
    user_1 = create_user(
        email='test1@test.com',
        password='test1',
    )
    user_2 = create_user(
        email='test2@test.com',
        password='test2',
    )
    wallet_1 = create_wallet(
        user=user_1,
        currency='USD',
        init_balance=Decimal(50),
    )
    wallet_2 = create_wallet(
        user=user_2,
        currency='RUB',
        init_balance=Decimal(0),
    )
    mocker.patch(
        'wallet.services.get_current_exchange_rate',
        return_value=Decimal('63.54563'),
    )
    mocker.patch(
        'wallet.services.increase_wallet_balance',
        side_effect=Exception,
    )

    # act
    with pytest.raises(Exception):
        transfer_money_between_wallets(
            sender=user_1,
            sender_wallet_id=wallet_1.pk,
            recipient_wallet_id=wallet_2.pk,
            amount=Decimal(10.0),
        )
    wallet_1 = Wallet.objects.get(pk=wallet_1.pk)
    wallet_2 = Wallet.objects.get(pk=wallet_2.pk)

    # assert
    assert wallet_1.balance == Decimal('50.00')
    assert wallet_2.balance == Decimal('0.00')


@pytest.mark.django_db
def test_retrieve_transactions_by_wallet_id__proper_call__return_transactions():
    # arrange
    user_1 = create_user(
        email='test1@test.com',
        password='test1',
    )
    user_2 = create_user(
        email='test2@test.com',
        password='test2',
    )
    wallet_1 = create_wallet(
        user=user_1,
        currency='USD',
        init_balance=Decimal(50),
    )
    wallet_2 = create_wallet(
        user=user_2,
        currency='RUB',
        init_balance=Decimal(0),
    )
    create_transaction(
        sender=wallet_1,
        recipient=wallet_2,
        amount=Decimal(10.0),
        exchange_rate=Decimal(63.54691),
    )
    create_transaction(
        sender=wallet_1,
        recipient=wallet_2,
        amount=Decimal(30.0),
        exchange_rate=Decimal(61.33420),
    )
    create_transaction(
        sender=wallet_2,
        recipient=wallet_1,
        amount=Decimal(300.0),
        exchange_rate=Decimal(0.01598),
    )

    # act
    transactions = retrieve_transactions_by_wallet_id(
        user=user_1,
        wallet_id=wallet_1.pk,
    )

    # assert
    assert len(transactions) == 3


@pytest.mark.django_db
def test_retrieve_transactions_by_wallet_id__user_do_not_own_wallet__raise_exception():
    # arrange
    user_1 = create_user(
        email='test1@test.com',
        password='test1',
    )

    # act & assert
    with pytest.raises(WalletOperationException):
        retrieve_transactions_by_wallet_id(
            user=user_1,
            wallet_id=100,
        )

import pytest
from decimal import Decimal

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.test import (
    APIRequestFactory,
    force_authenticate,
)

from api.views import (
    TransmitMoneyView,
    UserRegistrationView,
    WalletTransactionsView,
)
from customauth.models import CustomUser
from customauth.services import create_user
from wallet.services import (
    create_transaction,
    create_wallet,
)


@pytest.mark.django_db
def test_signin__unknown_user__return_bad_request():
    # arrange
    client = APIRequestFactory()
    data = {
        'username': 'test@test.com',
        'password': 'tester',
    }
    view = ObtainAuthToken.as_view()
    request = client.post(
        '/api/v1/signin/',
        data=data,
        format='json',
    )

    # act
    response = view(request)

    # assert
    assert response.status_code == 400


@pytest.mark.django_db
def test_signin__proper_call__return_token():
    # arrange
    CustomUser.objects.create_user(
        email='test@test.com',
        password='test',
    )
    client = APIRequestFactory()
    data = {
        'username': 'test@test.com',
        'password': 'test',
    }
    view = ObtainAuthToken.as_view()
    request = client.post(
        '/api/v1/signin/',
        data=data,
        format='json',
    )

    # act
    response = view(request)

    # assert
    assert response.status_code == 200
    assert 'token' in response.data.keys()


@pytest.mark.django_db
def test_signup__proper_call__return_200_and_message(mocker):
    # arrange
    client = APIRequestFactory()
    data = {
        'email': 'test@test.com',
        'password1': 'test',
        'password2': 'test',
        'currency': 'RUB',
        'init_balance': Decimal('50.00')
    }
    mocker.patch('api.views.create_user_and_wallet')
    view = UserRegistrationView.as_view()
    request = client.post(
        '/api/v1/signup/',
        data=data,
        format='json',
    )

    # act
    response = view(request)

    # assert
    assert response.status_code == 201
    assert response.data['status'] == 201
    assert response.data['message'] == 'User is successfully created'


@pytest.mark.django_db
def test_signup__value_error__return_400_and_exception_text(mocker):
    # arrange
    client = APIRequestFactory()
    data = {
        'email': 'test@test.com',
        'password1': 'test',
        'password2': 'test',
        'currency': 'RUB',
        'init_balance': Decimal('50.00')
    }
    mocker.patch(
        'api.views.create_user_and_wallet',
        side_effect=Exception('Something went wrong'),
    )
    view = UserRegistrationView.as_view()
    request = client.post(
        '/api/v1/signup/',
        data=data,
        format='json',
    )

    # act
    response = view(request)

    # assert
    assert response.status_code == 400
    assert response.data['error'] == 'Something went wrong'


@pytest.mark.django_db
def test_signup__email_unfilled__return_400_and_exception_raised(mocker):
    # arrange
    client = APIRequestFactory()
    data = {
        'password1': 'test',
        'password2': 'test',
        'currency': 'RUB',
        'init_balance': Decimal('50.00')
    }
    create_user_and_wallet_mocker = mocker.patch(
        'api.views.create_user_and_wallet',
    )
    view = UserRegistrationView.as_view()
    request = client.post(
        '/api/v1/signup/',
        data=data,
        format='json',
    )

    # act
    response = view(request)

    # assert
    assert response.status_code == 400
    assert response.data['status'] == 400
    create_user_and_wallet_mocker.assert_not_called()


@pytest.mark.django_db
def test_transfer_money__amount_unfilled__return_400_and_exception_raised(mocker):
    # arrange
    user = create_user(
        email='test@test.com',
        password='test',
    )
    transfer_money_between_wallets_mocker = mocker.patch(
        'api.views.transfer_money_between_wallets',
    )
    client = APIRequestFactory()
    data = {
        'sender': 100,
        'recipient': 101,
    }
    view = TransmitMoneyView.as_view()
    request = client.post(
        '/api/v1/transmit_money/',
        data=data,
        format='json',
    )
    force_authenticate(request, user=user)

    # act
    response = view(request)

    # assert
    assert response.status_code == 400
    assert response.data['status'] == 400
    transfer_money_between_wallets_mocker.assert_not_called()


@pytest.mark.django_db
def test_transfer_money__proper_call__return_200_and_message(mocker):
    # arrange
    user_1 = create_user(
        email='test@test.com',
        password='test',
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
    transfer_money_between_wallets_mocker = mocker.patch(
        'api.views.transfer_money_between_wallets',
    )
    client = APIRequestFactory()
    data = {
        'sender': wallet_1.pk,
        'recipient': wallet_2.pk,
        'amount': Decimal(40.5)
    }
    view = TransmitMoneyView.as_view()
    request = client.post(
        '/api/v1/transmit_money/',
        data=data,
        format='json',
    )
    force_authenticate(request, user=user_1)

    # act
    response = view(request)

    # assert
    assert response.status_code == 200
    assert response.data['status'] == 200
    transfer_money_between_wallets_mocker.assert_called_once_with(
        sender=user_1,
        sender_wallet_id=wallet_1.pk,
        recipient_wallet_id=wallet_2.pk,
        amount=Decimal(40.5),
    )


@pytest.mark.django_db
def test_transactions__proper_call__return_200_and_transactions(mocker):
    # arrange
    user_1 = create_user(
        email='test@test.com',
        password='test',
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
    transaction_1 = create_transaction(
        sender=wallet_1,
        recipient=wallet_2,
        amount=Decimal(10.0),
        exchange_rate=Decimal(63.54691),
    )
    transaction_2 = create_transaction(
        sender=wallet_1,
        recipient=wallet_2,
        amount=Decimal(30.0),
        exchange_rate=Decimal(61.33420),
    )
    transaction_3 = create_transaction(
        sender=wallet_2,
        recipient=wallet_1,
        amount=Decimal(300.0),
        exchange_rate=Decimal(0.01598),
    )
    retrieve_transactions_by_wallet_id_mocker = mocker.patch(
        'api.views.retrieve_transactions_by_wallet_id',
        return_value=[
            transaction_1,
            transaction_2,
            transaction_3,
        ],
    )
    client = APIRequestFactory()
    view = WalletTransactionsView.as_view()
    request = client.get(
        f'/api/v1/transactions/{wallet_1.pk}/',
        format='json',
    )
    force_authenticate(request, user=user_1)

    # act
    response = view(request, wallet_1.pk)

    # assert
    assert response.status_code == 200
    assert response.data['status'] == 200
    assert len(response.data['transactions']) == 3
    retrieve_transactions_by_wallet_id_mocker.assert_called_once_with(
        user=user_1,
        wallet_id=wallet_1.pk,
    )


@pytest.mark.django_db
def test_transactions__empty_transaction__return_200_and_empty_list(mocker):
    # arrange
    user_1 = create_user(
        email='test@test.com',
        password='test',
    )
    retrieve_transactions_by_wallet_id_mocker = mocker.patch(
        'api.views.retrieve_transactions_by_wallet_id',
        return_value=[],
    )
    client = APIRequestFactory()
    view = WalletTransactionsView.as_view()
    request = client.get(
        '/api/v1/transactions/100/',
        format='json',
    )
    force_authenticate(request, user=user_1)

    # act
    response = view(request, 100)

    # assert
    assert response.status_code == 200
    assert response.data['status'] == 200
    assert response.data['transactions'] == []
    retrieve_transactions_by_wallet_id_mocker.assert_called_once()


@pytest.mark.django_db
def test_transactions__exception_occured__return_400_and_error(mocker):
    # arrange
    user_1 = create_user(
        email='test@test.com',
        password='test',
    )
    retrieve_transactions_by_wallet_id_mocker = mocker.patch(
        'api.views.retrieve_transactions_by_wallet_id',
        side_effect=Exception,
    )
    client = APIRequestFactory()
    view = WalletTransactionsView.as_view()
    request = client.get(
        '/api/v1/transactions/100/',
        format='json',
    )
    force_authenticate(request, user=user_1)

    # act
    response = view(request, 100)

    # assert
    assert response.status_code == 400
    assert response.data['status'] == 400
    assert response.data['error'] is not None
    retrieve_transactions_by_wallet_id_mocker.assert_called_once()

import pytest
from decimal import Decimal

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.test import APIRequestFactory

from api.views import UserRegistrationView
from customauth.models import CustomUser


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

import pytest

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.test import APIRequestFactory

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

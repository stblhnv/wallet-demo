import pytest

from customauth.services import create_user


@pytest.mark.django_db
def test_create_user__proper_call__return_user():
    # arrange
    email = 'test@test.com'

    # act
    user = create_user(
        email=email,
        password='test',
    )

    # assert
    assert user.is_active is True
    assert user.is_staff is False
    assert user.email == email

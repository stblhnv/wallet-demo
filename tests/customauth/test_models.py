import pytest

from customauth.models import CustomUser


@pytest.mark.django_db
def test_create_user__proper_call__user_created():
    # act
    user = CustomUser.objects.create_user(
        email='test@test.com',
        password='test',
    )

    # assert
    assert user.email == 'test@test.com'
    assert user.is_active is True
    assert user.is_staff is False
    assert user.is_superuser is False


@pytest.mark.django_db
def test_create_user__email_is_none__raise_exception():
    # act & assert
    with pytest.raises(ValueError):
        CustomUser.objects.create_user(
            email=None,
            password='test',
        )


@pytest.mark.django_db
def test_create_superuser__proper_call__user_created():
    # act
    user = CustomUser.objects.create_superuser(
        email='test@test.com',
        password='test',
    )

    # assert
    assert user.email == 'test@test.com'
    assert user.is_active is True
    assert user.is_staff is True
    assert user.is_superuser is True


@pytest.mark.django_db
def test_create_superuser__email_is_none__raise_exception():
    # act & assert
    with pytest.raises(ValueError):
        CustomUser.objects.create_superuser(
            email=None,
            password='test',
        )

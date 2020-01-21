from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
)
from django.db import models


class UserManager(BaseUserManager):

    def create_user(self, email: str, password: str, **extra_fields) -> 'User':
        if not email:
            raise ValueError('User must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            is_staff=False,
            is_superuser=False,
            is_active=True,
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email: str, password: str, **extra_fields) -> 'User':
        if not email:
            raise ValueError('Superuser must have an email address')

        user = self.create_user(
            email,
            password=password,
            **extra_fields,
        )

        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class CustomUser(AbstractUser):

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    email = models.EmailField(
        max_length=150,
        unique=True,
        verbose_name='Email',
        help_text='Адрес электронной почты пользователя',
    )
    username = models.CharField(
        max_length=150,
        unique=False,
        blank=True,
        null=True,
        verbose_name='Username',
        help_text='Username',
    )

    def __str__(self):
        return self.email

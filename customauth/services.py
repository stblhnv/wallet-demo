from .models import CustomUser


def create_user(email: str, password: str) -> CustomUser:
    return CustomUser.objects.create_user(
        email=email,
        password=password,
    )

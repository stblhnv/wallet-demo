from decimal import Decimal

from customauth.models import CustomUser
from customauth.services import create_user
from wallet.exceptions import WalletCreationException
from wallet.services import create_wallet


def create_user_and_wallet(
        email: str,
        password: str,
        currency: str,
        init_balance: Decimal,
) -> CustomUser:
    # Предположим, что юзер может существовать без
    # кошелька, поэтому не оборачиваем в
    # transaction.atomic()
    user = create_user(
        email=email,
        password=password,
    )
    try:
        create_wallet(
            user=user,
            currency=currency,
            init_balance=init_balance,
        )
    except WalletCreationException:
        pass
    return user

from decimal import (
    Decimal,
    ROUND_HALF_DOWN,
)
from typing import (
    Dict,
    List,
)

from django.db import transaction
from django.db.models import Q

from customauth.models import CustomUser
from .exceptions import (
    ExchangeRateCreationException,
    WalletCreationException,
    WalletOperationException,
)
from .models import (
    CURRENCIES,
    ExchangeRate,
    Transaction,
    Wallet,
)
from .repositories.exchangeratesapi import get_exchange_rates


def create_exchange_rate(
        currency: str,
        exchange_rates: Dict[str, float],
) -> ExchangeRate:
    if currency in CURRENCIES and set(exchange_rates.keys()) - CURRENCIES == set():
        return ExchangeRate.objects.create(
            currency=currency,
            rates=exchange_rates,
        )
    raise ExchangeRateCreationException(
        f'Unknown currencies found among ({currency}, {exchange_rates}).',
    )


def update_exchange_rates() -> None:
    for currency in CURRENCIES:
        target_currencies = CURRENCIES - {currency}
        new_rates = get_exchange_rates(
            base_currency=currency,
            target_currencies=target_currencies,
        )
        create_exchange_rate(
            currency=currency,
            exchange_rates=new_rates,
        )


def create_wallet(
        user: CustomUser,
        currency: str,
        init_balance: Decimal,
) -> Wallet:
    if init_balance >= 0 and currency in CURRENCIES:
        cents = Decimal('.01')
        return Wallet.objects.create(
            owner=user,
            currency=currency,
            balance=Decimal(init_balance).quantize(cents, ROUND_HALF_DOWN),
        )
    raise WalletCreationException(
        'Unable to create wallet with negative balance or currency is unknown',
    )


def convert_amount(amount: Decimal, exchange_rate: Decimal) -> Decimal:
    cents = Decimal('.01')
    new_amount = Decimal(exchange_rate) * amount
    return new_amount.quantize(cents, ROUND_HALF_DOWN)


def decrease_wallet_balance(wallet: Wallet, amount: Decimal) -> None:
    if amount <= 0:
        raise WalletOperationException('Сумма должна быть больше нуля.')
    if amount > wallet.balance:
        raise WalletOperationException('Нельзя списать денег больше, чем у вас есть.')
    cents = Decimal('.01')
    wallet.balance -= amount.quantize(cents, ROUND_HALF_DOWN)
    wallet.save()


def increase_wallet_balance(wallet: Wallet, amount: Decimal) -> None:
    if amount <= 0:
        raise WalletOperationException('Сумма должна быть больше нуля.')
    cents = Decimal('.01')
    wallet.balance += amount.quantize(cents, ROUND_HALF_DOWN)
    wallet.save()


def create_transaction(
        sender: Wallet,
        recipient: Wallet,
        amount: Decimal,
        exchange_rate: Decimal,
) -> Transaction:
    return Transaction.objects.create(
        sender=sender,
        recipient=recipient,
        amount=amount,
        exchange_rate=exchange_rate,
    )


def get_current_exchange_rate(
        base_currency: str,
        target_currency: str,
) -> Decimal:
    if base_currency not in CURRENCIES or target_currency not in CURRENCIES:
        raise ValueError(
            f'Pair ({base_currency}, {target_currency}) is invalid.',
        )

    last_record = ExchangeRate.objects.filter(currency=base_currency).order_by('created_at').first()

    if last_record:
        accuracy = Decimal('.00001')
        return Decimal(last_record.rates[target_currency]).quantize(accuracy, ROUND_HALF_DOWN)

    raise ExchangeRate.DoesNotExist(
        f'No record for pair ({base_currency}, {target_currency}).',
    )


def transfer_money_between_wallets(
        sender: CustomUser,
        sender_wallet_id: int,
        recipient_wallet_id: int,
        amount: Decimal,
) -> Transaction:
    sender_wallets = sender.wallets.all()
    wallets_query = Wallet.objects.filter(
        pk__in=[sender_wallet_id, recipient_wallet_id],
    )
    wallets = {wallet.pk: wallet for wallet in wallets_query}

    if len(wallets) < 2:
        raise Wallet.DoesNotExist('Target wallet or you wallet does not exist.')

    sender_wallet, recipient_wallet = wallets[sender_wallet_id], wallets[recipient_wallet_id]

    if sender_wallet not in set(sender_wallets):
        raise WalletOperationException('This is not your wallet. Try again.')

    if sender_wallet.currency == recipient_wallet.currency:
        exchange_rate, amount_to_transfer = Decimal(1), amount
    else:
        exchange_rate = get_current_exchange_rate(
            base_currency=sender_wallet.currency,
            target_currency=recipient_wallet.currency,
        )
        amount_to_transfer = convert_amount(
            amount=amount,
            exchange_rate=exchange_rate,
        )

    with transaction.atomic():
        # оборачиваем, чтобы не высыпались деньги между кошельками
        decrease_wallet_balance(
            wallet=sender_wallet,
            amount=amount,
        )
        increase_wallet_balance(
            wallet=recipient_wallet,
            amount=amount_to_transfer,
        )
        created_transaction = create_transaction(
            sender=sender_wallet,
            recipient=recipient_wallet,
            amount=amount,
            exchange_rate=exchange_rate,
        )

    return created_transaction


def retrieve_transactions_by_wallet_id(
        user: CustomUser,
        wallet_id: int,
) -> List[Transaction]:
    user_wallets_ids = set(user.wallets.all().values_list('id', flat=True))
    if wallet_id in user_wallets_ids:
        transactions = Transaction.objects.filter(
            Q(sender_id=wallet_id) | Q(recipient_id=wallet_id),
        )
        return transactions
    raise WalletOperationException(
        'This is not your wallet',
    )

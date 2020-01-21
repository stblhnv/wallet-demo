from django.core.management.base import BaseCommand

from ...services import update_exchange_rates


class Command(BaseCommand):
    help = 'This command adds current currency rates to database'

    def handle(self, *args, **options):
        update_exchange_rates()

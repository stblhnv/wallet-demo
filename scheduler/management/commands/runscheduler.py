from django.core.management import BaseCommand

from ...scheduler import run_scheduler


class Command(BaseCommand):
    help = 'Run Advanced Python Scheduler in Django environment'

    def handle(self, *args, **options):
        run_scheduler()

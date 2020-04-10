import time

from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """django command to pause until db available"""

    def handle(self, *args, **options):
        self.stdout.write('waiting for db...')
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                self.stdout.write('db unavailable, waiting...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('db available'))

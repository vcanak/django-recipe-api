"""
Django command to wait for the database to be available.
"""
import time

from psycopg2 import OperationalError as Psycopg20pError

from django.core.management.base import BaseCommand
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Django command to wait for database."""

    def handle(self, *args, **options):
        """Entrypoint for command."""

        self.stdout.write('Waiting for db...')
        is_db_ready = False

        while is_db_ready is False:
            try:
                self.check(databases=['default'])
                is_db_ready = True
            except (Psycopg20pError, OperationalError):
                self.stdout.write('DB is unavailable, waiting 1 second...')
                time.sleep(1)
        time.sleep(1)
        self.stdout.write(self.style.SUCCESS('DB is available!'))

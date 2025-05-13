from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Tests all connections'

    def handle(self, *args, **options):

        self.stdout.write('Testing SQL connection...')
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.stdout.write(self.style.SUCCESS('SQL connection successful'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                'SQL connection failed: ' + str(e)))

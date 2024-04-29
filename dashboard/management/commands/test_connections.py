from django.core.management.base import BaseCommand
from django.db import connection
from neomodel import db

class Command(BaseCommand):
    help = 'Tests all connections'

    def handle(self, *args, **options):
        self.stdout.write('Testing Neo4j connection...')
        try:
            db.cypher_query("RETURN 1")
            self.stdout.write(self.style.SUCCESS('Neo4j connection successful'))
        except Exception as e:
            self.stdout.write(self.style.ERROR('Neo4j connection failed: ' + str(e)))

        self.stdout.write('Testing SQL connection...')
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.stdout.write(self.style.SUCCESS('SQL connection successful'))
        except Exception as e:
            self.stdout.write(self.style.ERROR('SQL connection failed: ' + str(e)))
from django.core.management import BaseCommand
from django.apps import apps


class Command(BaseCommand):
    help = 'Delete all data from all models in the database'

    def handle(self, *args, **kwargs):
        for model in apps.get_models():
            model.objects.all().delete()
        self.stdout.write('All data from all models has been deleted.')

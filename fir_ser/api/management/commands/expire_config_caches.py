from django.core.management.base import BaseCommand

from api.tasks import clean_config_cache


class Command(BaseCommand):
    help = 'Expire config caches'

    def handle(self, *args, **options):
        clean_config_cache()

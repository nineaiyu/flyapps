from django.core.management.base import BaseCommand

from api.tasks import clean_config_cache


class Command(BaseCommand):
    help = 'Expire config caches'

    def add_arguments(self, parser):
        parser.add_argument('key', nargs='?', type=str, default='*')

    def handle(self, *args, **options):
        clean_config_cache(options.get('key', '*'))

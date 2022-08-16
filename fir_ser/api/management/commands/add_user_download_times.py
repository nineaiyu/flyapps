from django.core.management.base import BaseCommand

from common.utils.caches import add_user_ds


class Command(BaseCommand):
    help = 'add user download times'

    def add_arguments(self, parser):
        parser.add_argument('uid', type=str, default='')
        parser.add_argument('download_times', type=int, default=100)

    def handle(self, *args, **options):
        add_user_ds(options.get('uid', None), options.get('download_times', 100))

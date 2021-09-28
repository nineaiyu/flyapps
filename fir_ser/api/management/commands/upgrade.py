from django.core.management.base import BaseCommand

from api.management.commands.services.hands import perform_db_migrate


class Command(BaseCommand):
    help = 'upgrade database'

    def handle(self, *args, **options):
        perform_db_migrate()

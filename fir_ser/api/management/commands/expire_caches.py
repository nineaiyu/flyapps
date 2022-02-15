from django.core.management.base import BaseCommand

from api.tasks import start_api_sever_do_clean
from xsign.utils.iproxy import clean_ip_proxy_infos


class Command(BaseCommand):
    help = 'Expire caches'

    def handle(self, *args, **options):
        start_api_sever_do_clean()
        clean_ip_proxy_infos()

from django.core.management.base import BaseCommand

from common.libs.mp.wechat import create_menu


class Command(BaseCommand):
    help = 'create weixin menu'

    def add_arguments(self, parser):
        parser.add_argument('menu_json', nargs='?', type=str, default=None)

    def handle(self, *args, **options):
        create_menu(options.get('menu_json', None))

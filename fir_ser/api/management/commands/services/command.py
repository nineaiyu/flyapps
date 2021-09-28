from django.core.management.base import BaseCommand, CommandError
from django.db.models import TextChoices
from .utils import ServicesUtil
from .hands import *


class Services(TextChoices):
    # gunicorn = 'gunicorn', 'gunicorn'
    uwsgi = 'uwsgi', 'uwsgi'
    celery = 'celery', 'celery'
    beat = 'beat', 'beat'
    flower = 'flower', 'flower'
    task = 'task', 'task'
    all = 'all', 'all'

    @classmethod
    def get_service_object_class(cls, name):
        from . import services
        services_map = {
            cls.flower: services.FlowerService,
            cls.celery: services.CeleryDefaultService,
            cls.beat: services.BeatService,
            cls.uwsgi: services.UwsgiService
        }
        return services_map.get(name)

    @classmethod
    def api_services(cls):
        return [cls.uwsgi]

    @classmethod
    def flower_services(cls):
        return [cls.flower]

    @classmethod
    def beat_services(cls):
        return [cls.beat]

    @classmethod
    def celery_services(cls):
        return [cls.celery]

    @classmethod
    def task_services(cls):
        return cls.celery_services() + cls.beat_services() + cls.flower_services()

    @classmethod
    def all_services(cls):
        return cls.task_services() + cls.api_services()

    @classmethod
    def export_services_values(cls):
        return [cls.all.value, cls.uwsgi.value, cls.task.value, cls.celery.value, cls.flower.value, cls.beat.value]

    @classmethod
    def get_service_objects(cls, service_names, **kwargs):
        services = set()
        for name in service_names:
            method_name = f'{name}_services'
            if hasattr(cls, method_name):
                _services = getattr(cls, method_name)()
            elif hasattr(cls, name):
                _services = [getattr(cls, name)]
            else:
                continue
            services.update(set(_services))

        service_objects = []
        for s in services:
            service_class = cls.get_service_object_class(s.value)
            if not service_class:
                continue
            kwargs.update({
                'name': s.value
            })
            service_object = service_class(**kwargs)
            service_objects.append(service_object)
        return service_objects


class Action(TextChoices):
    start = 'start', 'start'
    status = 'status', 'status'
    stop = 'stop', 'stop'
    restart = 'restart', 'restart'


class BaseActionCommand(BaseCommand):
    help = 'Service Base Command'

    action = None
    util = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            'services', nargs='+', choices=Services.export_services_values(), help='Service',
        )
        parser.add_argument('-d', '--daemon', nargs="?", const=True)
        parser.add_argument('-up', '--uwsgi_processes', type=int, nargs="?", default=4)
        parser.add_argument('-ut', '--uwsgi_threads', type=int, nargs="?", default=2)
        parser.add_argument('-usm', '--uwsgi_socket_mode', nargs="?", const=True,
                            help='run to bind socket mode, default http mode, only uwsgi service')
        parser.add_argument('-f', '--force', nargs="?", const=True)
        parser.add_argument('-u', '--uid', nargs="?", default='root', type=str)
        parser.add_argument('-g', '--gid', nargs="?", default='root', type=str)

    def initial_util(self, *args, **options):
        service_names = options.get('services')
        service_kwargs = {
            'uwsgi_processes': options.get('uwsgi_processes'),
            'uwsgi_threads': options.get('uwsgi_threads'),
            'uwsgi_socket_mode': options.get('uwsgi_socket_mode'),
            'uid': options.get('uid'),
            'gid': options.get('uid') if options.get('gid') in ['root'] else options.get('gid'),
        }
        services = Services.get_service_objects(service_names=service_names, **service_kwargs)

        kwargs = {
            'services': services,
            'run_daemon': options.get('daemon', False),
            'stop_daemon': self.action == Action.stop.value and Services.all.value in service_names,
            'force_stop': options.get('force') or False,
        }
        self.util = ServicesUtil(**kwargs)

    def handle(self, *args, **options):
        self.initial_util(*args, **options)
        assert self.action in Action.values, f'The action {self.action} is not in the optional list'
        _handle = getattr(self, f'_handle_{self.action}', lambda: None)
        _handle()

    def _handle_start(self):
        self.util.start_and_watch()
        os._exit(0)

    def _handle_stop(self):
        self.util.stop()

    def _handle_restart(self):
        self.util.restart()

    def _handle_status(self):
        self.util.show_status()

from django.core.cache import cache

from .base import BaseService
from ..hands import *

__all__ = ['BeatService']


class BeatService(BaseService):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lock = cache.lock('beat-distribute-start-lock', timeout=60)

    @property
    def cmd(self):
        scheduler = "django_celery_beat.schedulers:DatabaseScheduler"
        print("\n- Start Beat as Periodic Task Scheduler")
        cmd = [
            'celery', '-A',
            'fir_ser', 'beat',
            '-l', 'INFO',
            '--scheduler', scheduler,
            '--max-interval', '60'
        ]
        if self.uid:
            cmd.extend(['--uid', self.uid])
        if self.gid:
            cmd.extend(['--gid', self.gid])

        return cmd

    @property
    def cwd(self):
        return APPS_DIR

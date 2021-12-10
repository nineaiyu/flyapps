from .base import BaseService
from ..hands import *


class CeleryBaseService(BaseService):

    def __init__(self, queue, celery_num=10, **kwargs):
        super().__init__(**kwargs)
        self.queue = queue
        self.celery_num = celery_num

    @property
    def cmd(self):
        print('\n- Start Celery as Distributed Task Queue: {}'.format(self.queue.capitalize()))

        os.environ.setdefault('PYTHONOPTIMIZE', '1')
        os.environ.setdefault('ANSIBLE_FORCE_COLOR', 'True')

        if os.getuid() == 0:
            os.environ.setdefault('C_FORCE_ROOT', '1')
        server_hostname = os.environ.get("SERVER_HOSTNAME")
        if not server_hostname:
            server_hostname = '%n'

        cmd = [
            'celery', '-A',
            'fir_ser', 'worker',
            '-l', 'INFO',
            '-c', str(self.celery_num),
            '-Q', self.queue,
            '-n', f'{self.queue}@{server_hostname}'
        ]
        if self.uid:
            cmd.extend(['--uid', self.uid])
        if self.gid:
            cmd.extend(['--gid', self.gid])
        return cmd

    @property
    def cwd(self):
        return APPS_DIR

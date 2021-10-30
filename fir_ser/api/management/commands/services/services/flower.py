from .base import BaseService
from ..hands import *

__all__ = ['FlowerService']


class FlowerService(BaseService):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def cmd(self):
        print("\n- Start Flower as Task Monitor")

        if os.getuid() == 0:
            os.environ.setdefault('C_FORCE_ROOT', '1')
        cmd = [
            'celery', '-A',
            'fir_ser', 'flower',
            '-l', 'INFO',
            '--uid', self.uid,
            '--gid', self.gid,
            '--url_prefix=/flower',
            '--auto_refresh=False',
            '--max_tasks=1000',
            f'--address={CELERY_FLOWER_HOST}',
            f'--port={CELERY_FLOWER_PORT}',
            # '--basic_auth=flower:ninevenxxx'
            # '--tasks_columns=uuid,name,args,state,received,started,runtime,worker'
        ]
        return cmd

    @property
    def cwd(self):
        return APPS_DIR

from ..hands import *
from .base import BaseService

__all__ = ['UwsgiService']


class UwsgiService(BaseService):

    def __init__(self, **kwargs):
        self.processes = kwargs['uwsgi_processes']
        self.threads = kwargs['uwsgi_threads']
        self.uwsgi_socket_mode = kwargs['uwsgi_socket_mode']
        super().__init__(**kwargs)

    @property
    def cmd(self):
        if os.getuid() == 0:
            os.environ.setdefault('C_FORCE_ROOT', '1')
        print("\n- Start Uwsgi WSGI HTTP Server")
        bind = f'{SOCKET_HOST}:{SOCKET_PORT}'
        cmd = [
            'uwsgi',
            '--uid', self.uid,
            '--gid', self.gid,
            '--processes', f'{self.processes}',
            '--threads', f'{self.threads}',
            '--wsgi-file', f"{BASE_DIR}/fir_ser/wsgi.py",
            '--listen', '512',
            '--chdir', BASE_DIR,
            '--buffer-size', '65536',
            '--vacuum',
            '--enable-threads',
        ]

        if self.uwsgi_socket_mode:
            cmd.extend(['--socket', bind])
        else:
            cmd.extend(['--http', bind])
        if DEBUG:
            cmd.extend(['--touch-reload', BASE_DIR])
        return cmd

    @property
    def cwd(self):
        return APPS_DIR

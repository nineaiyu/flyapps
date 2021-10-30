#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月
# author: liuyu
# date: 2020/3/6
import json
import logging
import os
import signal
import socket
import time
from subprocess import Popen, PIPE

import paramiko

logger = logging.getLogger(__name__)


def default_result():
    return {'exit_code': '99', 'return_info': 'Failed to run, function_name is not existed'}


def portisonline(host, port):
    result = {}
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sk.settimeout(3)
    result["host"] = host
    result["port"] = port
    result["functionname"] = "CHECK_HOST_ONLINE："
    try:
        sk.connect((host, port))
        result["message"] = "Connection success"
        result["code"] = 0
    except Exception:
        result["message"] = "SSH Port Connection refused"
        result["code"] = 1
    sk.close()
    return result


class SSHConnection(object):
    def __init__(self, host, port, username, password):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._transport = None
        self._sftp = None
        self._client = None
        self._connect()

    def _connect(self):
        transport = paramiko.Transport((self._host, self._port))
        transport.connect(username=self._username, password=self._password)
        self._transport = transport

    # 下载
    def download(self, remotepath, localpath):
        if self._sftp is None:
            self._sftp = paramiko.SFTPClient.from_transport(self._transport)
        self._sftp.get(remotepath, localpath)
        self.close()

    # 上传
    def put(self, localpath, remotepath):
        if self._sftp is None:
            self._sftp = paramiko.SFTPClient.from_transport(self._transport)
        self.exec_command('mkdir -p %s' % (os.path.dirname(remotepath)))
        self._sftp.put(localpath, remotepath)
        self.close()

    # 执行命令
    def exec_command(self, command):
        if self._client is None:
            self._client = paramiko.SSHClient()
            self._client._transport = self._transport
        stdin, stdout, stderr = self._client.exec_command(command)
        data = stdout.read()
        if len(data) > 0:
            return {'status': 0, 'infos': data}
        err = stderr.read()
        if len(err) > 0:
            return {'status': 1, 'infos': err}
        return {'status': 0, 'infos': data}

    def close(self):
        if self._transport:
            self._transport.close()
        if self._client:
            self._client.close()


def shell_command(cmdstrs, timeout):
    result = default_result()
    result['return_info'] = ''
    shell_start_time = time.time()
    child = Popen(cmdstrs, shell=True, stdout=PIPE, stderr=PIPE)
    if timeout:
        while child.poll() is None:
            time.sleep(1)
            now = time.time()
            if int(now - shell_start_time) > timeout:
                os.kill(child.pid, signal.SIGKILL)
                os.waitpid(-1, os.WNOHANG)
                result['exit_code'] = 126
                return result

    out, err = child.communicate()
    if err:
        result['err_info'] = err.decode("utf-8")
    shell_end_time = time.time()
    result['shell_run_time'] = shell_end_time - shell_start_time
    out = out.strip(b'\n')
    result['return_info'] = out
    result['exit_code'] = child.returncode
    logger.info(f'shell: {cmdstrs} - return_info:{out} - exit_code:{child.returncode}')
    return result


def use_user_pass(hostip, port, user, passwd, cmdstrs):
    result = default_result()
    checkinfo = portisonline(hostip, port)
    if checkinfo["code"] != 0:
        result['shell_run_time'] = 0
        result['return_info'] = json.dumps(checkinfo)
        result['exit_code'] = checkinfo["code"]
    else:
        conn = SSHConnection(hostip, port, user, passwd)
        result['return_info'] = ''
        shell_start_time = time.time()
        out = conn.exec_command(cmdstrs)
        shell_end_time = time.time()
        result['shell_run_time'] = shell_end_time - shell_start_time
        outs = str(out['infos'], 'utf-8')
        outs = outs.strip('\n')
        result['return_info'] = outs
        result['exit_code'] = out['status']
        logger.info(f'host: {hostip} user:{user} - shell: {cmdstrs} - return_info:{out} - exit_code:{out["status"]}')
        conn.close()
    return result

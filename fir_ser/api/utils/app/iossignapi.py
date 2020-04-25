#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月
# author: liuyu
# date: 2020/4/24

from api.utils.app.shellcmds import shell_command,use_user_pass
from fir_ser.settings import SUPER_SIGN_ROOT
import os
from api.utils.app.randomstrings import make_app_uuid

def exec_shell(cmd,remote=False):
    if remote:
        hostip="10.66.6.66"
        port=65534
        user="root"
        passwd="root"
        result = use_user_pass(hostip,port,user,passwd,cmd)
        print(result)
        return result
    else:
        print(cmd)
        result = shell_command(cmd)
        print(result)
        if result.get("exit_code") != 0 :
            raise
        return result



class AppDeveloperApi(object):
    def __init__(self,username,password,certid):
        self.username = username
        self.password = password
        self.certid = certid
        script_path=os.path.join(SUPER_SIGN_ROOT,'scripts','apple_api.rb')
        self.cmd = "ruby %s '%s' '%s'" %(script_path,self.username,self.password)

    def create_cert(self,user_obj):
        cert_dir_name = make_app_uuid(user_obj,self.username)
        cert_dir_path = os.path.join(SUPER_SIGN_ROOT,cert_dir_name)
        if not os.path.isdir(cert_dir_path):
            os.makedirs(cert_dir_path)
        file_format_path_name = os.path.join(cert_dir_path,cert_dir_name)
        self.cmd=self.cmd + " cert add  '%s'" %(file_format_path_name)
        result = exec_shell(self.cmd)

    def get_profile(self,bundleId,app_id,device_udid,device_name,provisionName):
        self.cmd=self.cmd + " profile add '%s' '%s' '%s' '%s' '%s' '%s'" %(bundleId,app_id,device_udid,device_name,self.certid,provisionName)
        result = exec_shell(self.cmd)

    def del_profile(self,bundleId,app_id):
        self.cmd=self.cmd + " profile del '%s' '%s'" %(bundleId,app_id)
        result = exec_shell(self.cmd)

    def set_device_status(self,status,device_udid):
        if status == "enable":
            self.cmd=self.cmd + " device enable '%s'" %(device_udid)
        else:
            self.cmd=self.cmd + " device disable '%s'" %(device_udid)
        result = exec_shell(self.cmd)

    def add_device(self,device_udid,device_name):
        self.cmd=self.cmd + " device add '%s' '%s'" %(device_udid,device_name)
        result = exec_shell(self.cmd)

    def add_app(self,bundleId,app_id):
        self.cmd=self.cmd + " app add '%s' '%s'" %(bundleId,app_id)
        result = exec_shell(self.cmd)

    def del_app(self,bundleId):
        self.cmd=self.cmd + " app del '%s' " %(bundleId)
        result = exec_shell(self.cmd)

# appdev = AppDeveloperApi("hehehuyu521@163.com","Hehehuyu123")
# appdev.create_cert()
# appdev.get_profile('com.hehegames.NenJiangMaJiang',"e6f0c1aeee6853af9c21651654a812e7","6dd86c12ab5506a1f7e45b0f58b6b1448f5cdf54","iPad5,1")
# # e6f0c1aeee6853af9c21651654a812e7_dis.mobileprovision

class ResignApp(object):

    def __init__(self,my_local_key,app_dev_pem):
        self.my_local_key=my_local_key
        self.app_dev_pem = app_dev_pem
        # script_path=os.path.join(SUPER_SIGN_ROOT,'scripts','apple_api.rb')
        self.cmd = "isign  -c '%s'  -k '%s' " %(self.app_dev_pem,self.my_local_key)

    def sign(self,new_profile,org_ipa,new_ipa):

        self.cmd = self.cmd + " -p '%s' -o '%s'  '%s'" %(new_profile,new_ipa,org_ipa)
        result = exec_shell(self.cmd)

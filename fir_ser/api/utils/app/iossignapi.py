#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月
# author: liuyu
# date: 2020/4/24

from api.utils.app.shellcmds import shell_command,use_user_pass,pshell_command
from fir_ser.settings import SUPER_SIGN_ROOT
import os
from api.utils.app.randomstrings import make_app_uuid

def exec_shell(cmd,remote=False,timeout=None):
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
        result = shell_command(cmd,timeout)
        print(result)
        if result.get("exit_code") != 0 :
            err_info=result.get("err_info",None)
            if err_info:
                if "have access to this membership resource. Contact your team" in err_info:
                    result["err_info"]="You currently don't have access to this membership resource"
                else:
                    result["err_info"]="Unknown Error"
            return False,result
        return True,result



class AppDeveloperApi(object):
    def __init__(self,username,password,certid):
        self.username = username
        self.password = password
        self.certid = certid
        script_path=os.path.join(SUPER_SIGN_ROOT,'scripts','apple_api.rb')
        self.cmd = "ruby %s '%s' '%s'" %(script_path,self.username,self.password)

    def active(self,user_obj):
        self.cmd = self.cmd + " active "
        print(self.cmd)
        result={}
        try:
            result = pshell_command(self.cmd,user_obj,self.username)
            print(result)
            if result["exit_code"] == 0:
                return True,result
        except Exception as e:
            print(e)
        return False,result

    def file_format_path_name(self,user_obj):
        cert_dir_name = make_app_uuid(user_obj,self.username)
        cert_dir_path = os.path.join(SUPER_SIGN_ROOT,cert_dir_name)
        if not os.path.isdir(cert_dir_path):
            os.makedirs(cert_dir_path)
        return os.path.join(cert_dir_path,cert_dir_name)

    def create_cert(self,user_obj):
        self.cmd=self.cmd + " cert add  '%s'" %(self.file_format_path_name(user_obj))
        return exec_shell(self.cmd)

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

    def get_device(self,user_obj):
        self.cmd=self.cmd + " device get '%s' " %(self.file_format_path_name(user_obj))
        return exec_shell(self.cmd)

    def add_app(self,bundleId,app_id):
        self.cmd=self.cmd + " app add '%s' '%s'" %(bundleId,app_id)
        result = exec_shell(self.cmd)

    def del_app(self,bundleId,app_id):
        self.cmd=self.cmd + " app del '%s' '%s'" %(bundleId,app_id)
        result = exec_shell(self.cmd)


class ResignApp(object):

    def __init__(self,my_local_key,app_dev_pem):
        self.my_local_key=my_local_key
        self.app_dev_pem = app_dev_pem
        # script_path=os.path.join(SUPER_SIGN_ROOT,'scripts','apple_api.rb')
        self.cmd = "isign  -c '%s'  -k '%s' " %(self.app_dev_pem,self.my_local_key)

    def sign(self,new_profile,org_ipa,new_ipa):

        self.cmd = self.cmd + " -p '%s' -o '%s'  '%s'" %(new_profile,new_ipa,org_ipa)
        result = exec_shell(self.cmd)

#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月
# author: liuyu
# date: 2020/4/24
import OpenSSL

from api.utils.app.shellcmds import shell_command, use_user_pass, pshell_command
from fir_ser.settings import SUPER_SIGN_ROOT
import os
from api.utils.app.randomstrings import make_app_uuid
import logging
from api.utils.apple.appleapiv3 import AppStoreConnectApi

logger = logging.getLogger(__file__)
import base64
from OpenSSL.SSL import FILETYPE_PEM
from OpenSSL.crypto import (dump_certificate_request, dump_privatekey, PKey, TYPE_RSA, X509Req, dump_certificate)


def exec_shell(cmd, remote=False, timeout=None):
    if remote:
        hostip = "10.66.6.66"
        port = 65534
        user = "root"
        passwd = "root"
        result = use_user_pass(hostip, port, user, passwd, cmd)
        return result
    else:
        logger.info("exec_shell cmd:%s" % (cmd))
        result = shell_command(cmd, timeout)
        logger.info("exec_shell cmd:%s  result:%s" % (cmd, result))
        if result.get("exit_code") != 0:
            err_info = result.get("err_info", None)
            if err_info:
                if "have access to this membership resource. Contact your team" in err_info:
                    result["err_info"] = "You currently don't have access to this membership resource 【您没有权限执行该操作】"
                elif "Maximum number of certificates generated" in err_info:
                    result["err_info"] = "Maximum number of certificates generated 【开发证书数量到上限】"
                else:
                    result["err_info"] = "Unknown Error"
            return False, result
        return True, result


class AppDeveloperApi(object):
    def __init__(self, username, password, certid):
        self.username = username
        self.password = password
        self.certid = certid
        script_path = os.path.join(SUPER_SIGN_ROOT, 'scripts', 'apple_api.rb')
        self.cmd = "ruby %s '%s' '%s'" % (script_path, self.username, self.password)

    def active(self, user_obj):
        self.cmd = self.cmd + " active "
        logger.info("ios developer active cmd:%s" % (self.cmd))
        result = {}
        try:
            result = pshell_command(self.cmd, user_obj, self.username)
            logger.info("ios developer active cmd:%s  result:%s" % (self.cmd, result))
            if result["exit_code"] == 0:
                return True, result
        except Exception as e:
            logger.error("ios developer active cmd:%s Failed Exception:%s" % (self.cmd, e))
        return False, result

    def file_format_path_name(self, user_obj):
        cert_dir_name = make_app_uuid(user_obj, self.username)
        cert_dir_path = os.path.join(SUPER_SIGN_ROOT, cert_dir_name)
        if not os.path.isdir(cert_dir_path):
            os.makedirs(cert_dir_path)
        return os.path.join(cert_dir_path, cert_dir_name)

    def create_cert(self, user_obj):
        self.cmd = self.cmd + " cert add  '%s'" % (self.file_format_path_name(user_obj))
        return exec_shell(self.cmd)

    def get_profile(self, bundleId, app_id, device_udid, device_name, provisionName, auth=None, first_sign=None,
                    device_id_list=None):
        self.cmd = self.cmd + " profile add '%s' '%s' '%s' '%s' '%s' '%s'" % (
            bundleId, app_id, device_udid, device_name, self.certid, provisionName)
        return exec_shell(self.cmd)

    def del_profile(self, bundleId, app_id):
        self.cmd = self.cmd + " profile del '%s' '%s'" % (bundleId, app_id)
        result = exec_shell(self.cmd)

    def set_device_status(self, status, device_udid):
        if status == "enable":
            self.cmd = self.cmd + " device enable '%s'" % (device_udid)
        else:
            self.cmd = self.cmd + " device disable '%s'" % (device_udid)
        result = exec_shell(self.cmd)

    def add_device(self, device_udid, device_name):
        self.cmd = self.cmd + " device add '%s' '%s'" % (device_udid, device_name)
        result = exec_shell(self.cmd)

    def get_device(self, user_obj):
        self.cmd = self.cmd + " device get '%s' " % (self.file_format_path_name(user_obj))
        return exec_shell(self.cmd)

    def create_app(self, bundleId, app_id):
        self.cmd = self.cmd + " app add '%s' '%s'" % (bundleId, app_id)
        result = exec_shell(self.cmd)

    def del_app(self, bundleId, app_id):
        self.cmd = self.cmd + " app del '%s' '%s'" % (bundleId, app_id)
        result = exec_shell(self.cmd)


class ResignApp(object):

    def __init__(self, my_local_key, app_dev_pem):
        self.my_local_key = my_local_key
        self.app_dev_pem = app_dev_pem
        # script_path=os.path.join(SUPER_SIGN_ROOT,'scripts','apple_api.rb')
        self.cmd = "isign  -c '%s'  -k '%s' " % (self.app_dev_pem, self.my_local_key)

    @staticmethod
    def sign_mobileconfig(mobilconfig_path, sign_mobilconfig_path, ssl_pem_path, ssl_key_path):
        cmd = "openssl smime -sign -in %s -out %s -signer %s " \
              "-inkey %s -certfile %s -outform der -nodetach " % (
                  mobilconfig_path, sign_mobilconfig_path, ssl_pem_path, ssl_key_path, ssl_pem_path)
        return exec_shell(cmd)

    def sign(self, new_profile, org_ipa, new_ipa, info_plist_properties=None):
        if info_plist_properties is None:
            info_plist_properties = {}
        properties = ""
        for k, v in info_plist_properties.items():
            properties += "%s=%s," % (k, v)
        if properties:
            properties = " -i '%s' " % properties[0:-1]
        self.cmd = self.cmd + " %s -p '%s' -o '%s'  '%s'" % (properties, new_profile, new_ipa, org_ipa)
        return exec_shell(self.cmd)


class AppDeveloperApiV2(object):
    def __init__(self, issuer_id, private_key_id, p8key, certid):
        self.issuer_id = issuer_id
        self.private_key_id = private_key_id
        self.p8key = p8key
        self.certid = certid

    def active(self, user_obj):
        result = {}
        try:
            apple_obj = AppStoreConnectApi(self.issuer_id, self.private_key_id, self.p8key)
            certificates = apple_obj.get_all_certificates()
            logger.info("ios developer active result:%s" % certificates)
            if len(certificates) > 0:
                return True, result
        except Exception as e:
            logger.error("ios developer active Failed Exception:%s" % e)
            result['return_info'] = "%s" % e
        return False, result

    def file_format_path_name(self, user_obj):
        cert_dir_name = make_app_uuid(user_obj, self.issuer_id)
        cert_dir_path = os.path.join(SUPER_SIGN_ROOT, cert_dir_name)
        if not os.path.isdir(cert_dir_path):
            os.makedirs(cert_dir_path)
        return os.path.join(cert_dir_path, cert_dir_name)

    def make_csr_content(self, csr_file_path, private_key_path):
        # create public/private key
        key = PKey()
        key.generate_key(TYPE_RSA, 2048)
        # Generate CSR
        req = X509Req()
        req.get_subject().CN = 'FLY APP'
        req.get_subject().O = 'FLY APP Inc'
        req.get_subject().OU = 'IT'
        req.get_subject().L = 'BJ'
        req.get_subject().ST = 'BJ'
        req.get_subject().C = 'CN'
        req.get_subject().emailAddress = 'fly@fly.com'
        req.set_pubkey(key)
        req.sign(key, 'sha256')
        csr_content = dump_certificate_request(FILETYPE_PEM, req)
        with open(csr_file_path, 'wb+') as f:
            f.write(csr_content)
        with open(private_key_path, 'wb+') as f:
            f.write(dump_privatekey(FILETYPE_PEM, key))

        return csr_content

    def make_pem(self, cer_content, pem_path):
        cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, cer_content)
        with open(pem_path, 'wb+') as f:
            f.write(dump_certificate(FILETYPE_PEM, cert))

    def create_cert(self, user_obj):
        result = {}
        try:
            apple_obj = AppStoreConnectApi(self.issuer_id, self.private_key_id, self.p8key)
            csr_path = self.file_format_path_name(user_obj)
            if not os.path.isdir(os.path.dirname(csr_path)):
                os.makedirs(os.path.dirname(csr_path))
            csr_content = self.make_csr_content(csr_path + ".csr", csr_path + ".key")
            certificates = apple_obj.create_certificate(csr_content.decode("utf-8"))
            if certificates:
                n = base64.b64decode(certificates.certificateContent)
                with open(csr_path + ".cer", 'wb') as f:
                    f.write(n)
                self.make_pem(n, csr_path + ".pem")
                logger.info("ios developer create  result:%s" % certificates.certificateContent)
                return True, certificates
        except Exception as e:
            logger.error("ios developer active Failed Exception:%s" % e)
            result['return_info'] = "%s" % e
        return False, result

    def get_profile(self, app_obj, udid_info, provisionName, auth, developer_app_id,
                    device_id_list):
        result = {}
        bundle_id = app_obj.bundle_id
        app_id = app_obj.app_id
        try:
            apple_obj = AppStoreConnectApi(self.issuer_id, self.private_key_id, self.p8key)
            if developer_app_id:
                pass
                # bundle_obj = apple_obj.register_bundle_id_enable_capability(app_id, bundleId + app_id)
            else:
                # bundle_obj = apple_obj.list_bundle_ids_by_identifier(bundleId + app_id)
                if app_obj.supersign_type == 0:
                    bundle_obj = apple_obj.register_bundle_id(app_id, bundle_id + app_id)
                else:
                    bundle_obj = apple_obj.register_bundle_id_enable_capability(app_id, bundle_id + app_id)
                developer_app_id = bundle_obj.id
                result['aid'] = developer_app_id
            if udid_info:
                device_udid = udid_info.get('udid')
                device_name = udid_info.get('product')
                device_obj = apple_obj.register_device(device_name, device_udid)
                if device_obj:
                    result['did'] = device_obj.id
                    device_id_list.append(device_obj.id)

            profile_obj = apple_obj.create_profile(developer_app_id, auth.get('certid'),
                                                   provisionName.split("/")[-1],
                                                   device_id_list)
            if profile_obj:
                n = base64.b64decode(profile_obj.profileContent)
                if not os.path.isdir(os.path.dirname(provisionName)):
                    os.makedirs(os.path.dirname(provisionName))
                with open(provisionName, 'wb') as f:
                    f.write(n)
                return True, result
        except Exception as e:
            logger.error("ios developer make profile Failed Exception:%s" % e)
            result['return_info'] = "%s" % e
            return False, result

    def del_profile(self, bundleId, app_id):
        result = {}
        try:
            apple_obj = AppStoreConnectApi(self.issuer_id, self.private_key_id, self.p8key)
            profile_obj = apple_obj.list_profile_by_profile_name(app_id)
            if profile_obj:
                if apple_obj.delete_profile_by_id(profile_obj.id):
                    return True, profile_obj
        except Exception as e:
            logger.error("ios developer delete profile Failed Exception:%s" % e)
            result['return_info'] = "%s" % e
            return False, result

    def set_device_status(self, status, device_udid):
        result = {}
        try:
            apple_obj = AppStoreConnectApi(self.issuer_id, self.private_key_id, self.p8key)
            if status == "enable":
                device_obj = apple_obj.enabled_device(device_udid)
            else:
                device_obj = apple_obj.disabled_device(device_udid)
            logger.info("device_obj %s result:%s" % (device_obj, status))
            if device_obj and device_obj.id:
                return True, result
        except Exception as e:
            logger.error("ios developer set devices status Failed Exception:%s" % e)
            result['return_info'] = "%s" % e
        return False, result

    def get_device(self, user_obj):
        result = {}
        try:
            apple_obj = AppStoreConnectApi(self.issuer_id, self.private_key_id, self.p8key)
            devices_obj_list = apple_obj.list_enabled_devices()
            if devices_obj_list:
                return True, devices_obj_list
        except Exception as e:
            logger.error("ios developer delete profile Failed Exception:%s" % e)
            result['return_info'] = "%s" % e
            return False, result

    def del_app(self, bundleId, app_id):
        result = {}
        try:
            apple_obj = AppStoreConnectApi(self.issuer_id, self.private_key_id, self.p8key)
            if apple_obj.delete_bundle_by_identifier(bundleId + app_id):
                return True, {}

        except Exception as e:
            logger.error("ios developer delete profile Failed Exception:%s" % e)
            result['return_info'] = "%s" % e
            return False, result

    def create_app(self, bundleId, app_id):
        result = {}
        try:
            apple_obj = AppStoreConnectApi(self.issuer_id, self.private_key_id, self.p8key)
            bundle_obj = apple_obj.register_bundle_id_enable_capability(app_id, bundleId + app_id)
            developer_app_id = bundle_obj.id
            result['aid'] = developer_app_id
            return True, result

        except Exception as e:
            logger.error("ios developer create app Failed Exception:%s" % e)
            result['return_info'] = "%s" % e
            return False, result

    def modify_capability(self, app_obj, developer_app_id):
        bundle_id = app_obj.bundle_id
        app_id = app_obj.app_id
        result = {}
        try:
            apple_obj = AppStoreConnectApi(self.issuer_id, self.private_key_id, self.p8key)
            if developer_app_id:
                if app_obj.supersign_type == 0:
                    result['code'] = apple_obj.disable_push_vpn_capability(developer_app_id)
                else:
                    result['code'] = apple_obj.enable_push_vpn_capability(developer_app_id)
            else:
                if app_obj.supersign_type == 0:
                    bundle_obj = apple_obj.register_bundle_id(app_id, bundle_id + app_id)
                else:
                    bundle_obj = apple_obj.register_bundle_id_enable_capability(app_id, bundle_id + app_id)
                developer_app_id = bundle_obj.id
                result['aid'] = developer_app_id
            return True, result
        except Exception as e:
            logger.error("ios developer modify_capability Failed Exception:%s" % e)
            result['return_info'] = "%s" % e
            return False, result

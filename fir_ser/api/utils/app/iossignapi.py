#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月
# author: liuyu
# date: 2020/4/24
import base64
import datetime
import logging
import os
import re

from OpenSSL.crypto import (load_pkcs12, dump_certificate_request, dump_privatekey, PKey, TYPE_RSA, X509Req,
                            dump_certificate, load_privatekey, load_certificate, PKCS12, FILETYPE_PEM, FILETYPE_ASN1)

from api.utils.app.shellcmds import shell_command, use_user_pass
from api.utils.apple.appleapiv3 import AppStoreConnectApi
from api.utils.baseutils import get_format_time, format_apple_date, make_app_uuid
from api.utils.storage.caches import CleanErrorBundleIdSignDataState
from fir_ser.settings import SUPER_SIGN_ROOT

logger = logging.getLogger(__name__)


def exec_shell(cmd, remote=False, timeout=None):
    if remote:
        host_ip = "10.66.6.66"
        port = 65534
        user = "root"
        passwd = "root"
        result = use_user_pass(host_ip, port, user, passwd, cmd)
        return result
    else:
        logger.info(f"exec_shell cmd:{cmd}")
        result = shell_command(cmd, timeout)
        logger.info(f"exec_shell cmd:{cmd}  result:{result}")
        if result.get("exit_code") != 0:
            err_info = result.get("err_info", None)
            if err_info:
                logger.error(f"exec_shell cmd:{cmd}  failed: {err_info}")
                result["err_info"] = "Unknown Error"
            return False, result
        return True, result


class ResignApp(object):

    def __init__(self, my_local_key, app_dev_pem, app_dev_p12):
        self.my_local_key = my_local_key
        self.app_dev_pem = app_dev_pem
        self.app_dev_p12 = app_dev_p12
        self.cmd = "zsign  -c '%s'  -k '%s' " % (self.app_dev_pem, self.my_local_key)

    @staticmethod
    def sign_mobile_config(sign_data, ssl_pem_path, ssl_key_path):
        """
        :param sign_data:  签名的数据
        :param ssl_pem_path:    pem证书的绝对路径
        :param ssl_key_path:    key证书的绝对路径
        :return:
        """
        #
        # cmd = "openssl smime -sign -in %s -out %s -signer %s " \
        #       "-inkey %s -certfile %s -outform der -nodetach " % (
        #           mobile_config_path, sign_mobile_config_path, ssl_pem_path, ssl_key_path, ssl_pem_path)
        # return exec_shell(cmd)
        result = {}
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.serialization import pkcs7
        from cryptography import x509
        try:
            cert_list = re.findall('-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----',
                                   open(ssl_pem_path, 'r').read(), re.S)
            if len(cert_list) == 0:
                raise Exception('load cert failed')
            else:
                cert = x509.load_pem_x509_certificate(cert_list[0].encode('utf-8'))
                cas = [cert]
                if len(cert_list) > 1:
                    cas.extend([x509.load_pem_x509_certificate(x.encode('utf-8')) for x in cert_list[1:]])
                key = serialization.load_pem_private_key(open(ssl_key_path, 'rb').read(), None)
                result['data'] = pkcs7.PKCS7SignatureBuilder(
                    data=sign_data.encode('utf-8'),
                    signers=[
                        (cert, key, hashes.SHA512()),
                    ],
                    additional_certs=cas,
                ).sign(
                    serialization.Encoding.DER, options=[],
                )
        except Exception as e:
            result['err_info'] = str(e)
            return False, result
        return True, result

    def make_p12_from_cert(self, password):
        result = {}
        try:
            certificate = load_certificate(FILETYPE_PEM, open(self.app_dev_pem, 'rb').read())
            private_key = load_privatekey(FILETYPE_PEM, open(self.my_local_key, 'rb').read())
            p12 = PKCS12()
            p12.set_certificate(certificate)
            p12.set_privatekey(private_key)
            with open(self.app_dev_p12, 'wb+') as f:
                f.write(p12.export(password))
            if password:
                with open(self.app_dev_p12 + '.pwd', 'w') as f:
                    f.write(password)
            return True, p12.get_friendlyname()
        except Exception as e:
            result["err_info"] = e
            return False, result

    def check_p12_exists(self):
        return os.path.exists(self.app_dev_p12)

    def write_cert(self):
        for file in [self.app_dev_p12, self.app_dev_p12 + '.pwd', self.my_local_key, self.app_dev_pem]:
            if os.path.exists(file):
                os.rename(file, file + '.' + get_format_time() + '.bak')
            os.rename(file + '.bak', file)

    def make_cert_from_p12(self, password, p12_content=None):
        result = {}
        try:
            if p12_content:
                p12_content_list = p12_content.split('data:application/x-pkcs12;base64,')
                if len(p12_content_list) == 2:
                    with open(self.app_dev_p12 + '.bak', 'wb+') as f:
                        f.write(base64.b64decode(p12_content.split('data:application/x-pkcs12;base64,')[1]))
                    if password:
                        with open(self.app_dev_p12 + '.pwd.bak', 'w') as f:
                            f.write(password)
                else:
                    result["err_info"] = '非法p12证书文件，请检查'
                    return False, result
            else:
                result["err_info"] = '证书内容有误，请检查'
                return False, result
            p12 = load_pkcs12(open(self.app_dev_p12 + '.bak', 'rb').read(), password)
            cert = p12.get_certificate()
            if cert.has_expired():
                result["err_info"] = '证书已经过期'
                return False, result
            with open(self.my_local_key + '.bak', 'wb+') as f:
                f.write(dump_privatekey(FILETYPE_PEM, p12.get_privatekey()))
            with open(self.app_dev_pem + '.bak', 'wb+') as f:
                f.write(dump_certificate(FILETYPE_PEM, cert))
            return True, cert.get_version()
        except Exception as e:
            for file in [self.app_dev_p12, self.app_dev_p12 + '.pwd', self.my_local_key, self.app_dev_pem]:
                if os.path.exists(file + '.bak'):
                    os.remove(file + '.bak')
            result["err_info"] = str(e)
            if 'mac verify failure' in str(e):
                result["err_info"] = 'p12 导入密码错误，请检查'
            return False, result

    def sign(self, new_profile, org_ipa, new_ipa, info_plist_properties=None):
        if info_plist_properties is None:
            info_plist_properties = {}
        properties = ""
        for k, v in info_plist_properties.items():
            properties += " %s '%s' " % (k, v)
        self.cmd = self.cmd + " %s -m '%s' -o '%s' -z 9 '%s'" % (properties, new_profile, new_ipa, org_ipa)
        return exec_shell(self.cmd)


def make_csr_content(csr_file_path, private_key_path):
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
    req.get_subject().emailAddress = 'flyapps@126.com'
    req.set_pubkey(key)
    req.sign(key, 'sha256')
    csr_content = dump_certificate_request(FILETYPE_PEM, req)
    with open(csr_file_path, 'wb+') as f:
        f.write(csr_content)
    with open(private_key_path, 'wb+') as f:
        f.write(dump_privatekey(FILETYPE_PEM, key))

    return csr_content


def make_pem(cer_content, pem_path):
    cert = load_certificate(FILETYPE_ASN1, cer_content)
    with open(pem_path, 'wb+') as f:
        f.write(dump_certificate(FILETYPE_PEM, cert))


class AppDeveloperApiV2(object):
    def __init__(self, issuer_id, private_key_id, p8key, cert_id):
        self.issuer_id = issuer_id
        self.private_key_id = private_key_id
        self.p8key = p8key
        self.cert_id = cert_id

    def active(self):
        result = {'data': []}
        try:
            apple_obj = AppStoreConnectApi(self.issuer_id, self.private_key_id, self.p8key)
            certificates = apple_obj.get_all_certificates()
            if not isinstance(certificates, list):
                certificates = [certificates]
            result['data'] = certificates
            logger.info(f"ios developer active result:{certificates}")
            if len(certificates) >= 0:
                return True, result
        except Exception as e:
            logger.error(f"ios developer active Failed Exception:{e}")
            result['return_info'] = "%s" % e
        return False, result

    def file_format_path_name(self, user_obj):
        cert_dir_name = make_app_uuid(user_obj, self.issuer_id)
        cert_dir_path = os.path.join(SUPER_SIGN_ROOT, cert_dir_name)
        if not os.path.isdir(cert_dir_path):
            os.makedirs(cert_dir_path)
        return os.path.join(cert_dir_path, cert_dir_name)

    def create_cert(self, user_obj):
        result = {}
        try:
            apple_obj = AppStoreConnectApi(self.issuer_id, self.private_key_id, self.p8key)
            csr_path = self.file_format_path_name(user_obj)
            if not os.path.isdir(os.path.dirname(csr_path)):
                os.makedirs(os.path.dirname(csr_path))
            csr_content = make_csr_content(csr_path + ".csr", csr_path + ".key")
            certificates = apple_obj.create_certificate(csr_content.decode("utf-8"))
            if certificates:
                n = base64.b64decode(certificates.certificateContent)
                with open(csr_path + ".cer", 'wb') as f:
                    f.write(n)
                make_pem(n, csr_path + ".pem")
                logger.info(f"ios developer create cert result:{certificates.certificateContent}")
                return True, certificates
        except Exception as e:
            logger.error(f"ios developer create cert Failed Exception:{e}")
            result['return_info'] = "%s" % e
        return False, result

    def get_cert_obj_by_cid(self):
        result = {}
        try:
            apple_obj = AppStoreConnectApi(self.issuer_id, self.private_key_id, self.p8key)
            cert_obj = apple_obj.get_certificate_by_cid(self.cert_id)
            if cert_obj and cert_obj.id:
                return True, result
            else:
                logger.info(f"ios developer get cert {self.cert_id} failed")
                return False, result
        except Exception as e:
            logger.error(f"ios developer get cert {self.cert_id} Failed Exception:{e}")
            result['return_info'] = "%s" % e
        return False, result

    def revoke_cert(self):
        result = {}
        try:
            apple_obj = AppStoreConnectApi(self.issuer_id, self.private_key_id, self.p8key)
            cert_obj = apple_obj.get_certificate_by_cid(self.cert_id)
            if cert_obj:
                s_date = format_apple_date(cert_obj.expirationDate)
                if s_date.timestamp() - datetime.datetime.now().timestamp() < 3600 * 24 * 3:
                    if apple_obj.revoke_certificate(self.cert_id):
                        logger.info(f"ios developer cert {self.cert_id} revoke")
                        return True, result
                else:
                    logger.info(f"ios developer cert {self.cert_id} not revoke.because expire time < 3 day ")
                    return True, result
        except Exception as e:
            logger.error(f"ios developer cert {self.cert_id} revoke Failed Exception:{e}")
            result['return_info'] = "%s" % e
        return False, result

    def auto_set_certid_by_p12(self, app_dev_pem):
        result = {}
        try:
            cer = load_certificate(FILETYPE_PEM, open(app_dev_pem, 'rb').read())
            not_after = datetime.datetime.strptime(cer.get_notAfter().decode('utf-8'), "%Y%m%d%H%M%SZ")
            apple_obj = AppStoreConnectApi(self.issuer_id, self.private_key_id, self.p8key)
            certificates = apple_obj.get_all_certificates()
            if not isinstance(certificates, list):
                certificates = [certificates]
            for cert_obj in certificates:
                f_date = format_apple_date(cert_obj.expirationDate)
                logger.info(f"{cert_obj.id}-{not_after.timestamp()} - {f_date.timestamp()} ")
                if not_after.timestamp() == f_date.timestamp():
                    return True, cert_obj
            return False, result
        except Exception as e:
            logger.error(f"ios developer cert {app_dev_pem} auto get Failed Exception:{e}")
            result['return_info'] = "%s" % e
        return False, result

    def del_profile(self, profile_id, profile_name):
        result = {}
        try:
            apple_obj = AppStoreConnectApi(self.issuer_id, self.private_key_id, self.p8key)
            if apple_obj.delete_profile_by_id(profile_id, profile_name):
                return True
        except Exception as e:
            logger.error(f"ios developer delete profile Failed Exception:{e}")
            result['return_info'] = "%s" % e
            return False, result

    def set_device_status(self, status, device_id, device_name, device_udid, failed_call_prefix,
                          device_err_callback=None):
        result = {}
        try:
            apple_obj = AppStoreConnectApi(self.issuer_id, self.private_key_id, self.p8key)
            if status == "enable":
                device_obj = apple_obj.enabled_device(device_id, device_name, device_udid)
            else:
                device_obj = apple_obj.disabled_device(device_id, device_name, device_udid)
            logger.info("device_obj %s result:%s" % (device_obj, status))
            if device_obj and device_obj.id:
                return True, result
        except Exception as e:
            logger.error("ios developer set devices status Failed Exception:%s" % e)
            result['return_info'] = "%s" % e
            if device_err_callback and ("There are no current ios devices" in str(e) or "Device obj is None" in str(e)):
                CleanErrorBundleIdSignDataState.set_state(failed_call_prefix)
                device_err_callback()
                CleanErrorBundleIdSignDataState.del_state(failed_call_prefix)
        return False, result

    def get_device(self):
        result = {}
        try:
            apple_obj = AppStoreConnectApi(self.issuer_id, self.private_key_id, self.p8key)
            devices_obj_list = apple_obj.get_all_devices()
            if devices_obj_list is not None:
                return True, devices_obj_list
        except Exception as e:
            logger.error("ios developer get device Failed Exception:%s" % e)
            result['return_info'] = "%s" % e
            return False, result

    def del_app(self, identifier_id, bundle_id, app_id):
        result = {}
        try:
            apple_obj = AppStoreConnectApi(self.issuer_id, self.private_key_id, self.p8key)
            if apple_obj.delete_bundle_by_identifier(identifier_id, f"{bundle_id}.{self.issuer_id}.{app_id}"):
                return True, {}

        except Exception as e:
            logger.error("ios developer delete app Failed Exception:%s" % e)
            result['return_info'] = "%s" % e
            return False, result

    def create_app(self, bundle_id, app_id, s_type, app_id_err_callback=None):
        if app_id_err_callback is None:
            app_id_err_callback = []
        result = {}
        try:
            result = {}
            apple_obj = AppStoreConnectApi(self.issuer_id, self.private_key_id, self.p8key)
            if s_type == 0:
                bundle_obj = apple_obj.register_bundle_id(app_id, f"{bundle_id}.{self.issuer_id}.{app_id}")
            else:
                bundle_obj = apple_obj.register_bundle_id_enable_capability(app_id,
                                                                            f"{bundle_id}.{self.issuer_id}.{app_id}",
                                                                            s_type)
            result['aid'] = bundle_obj.id
            return True, result

        except Exception as e:
            logger.error("ios developer create app Failed Exception:%s" % e)
            result['return_info'] = "%s" % e
            if app_id_err_callback and "There is no App ID with ID" in str(e):
                for call_fun in app_id_err_callback:
                    call_fun()
            return False, result

    def register_device(self, device_udid, device_name, failed_call_prefix, device_err_callback=None):
        result = {}
        try:
            apple_obj = AppStoreConnectApi(self.issuer_id, self.private_key_id, self.p8key)
            return True, apple_obj.register_device(device_name, device_udid)
        except Exception as e:
            logger.error("ios developer register device Failed Exception:%s" % e)
            result['return_info'] = "%s" % e
            if device_err_callback and "There are no current ios devices" in str(e):
                CleanErrorBundleIdSignDataState.set_state(failed_call_prefix)
                device_err_callback()
                CleanErrorBundleIdSignDataState.del_state(failed_call_prefix)
            return False, result

    def make_and_download_profile(self, app_obj, provision_name, auth, developer_app_id, device_id_list, profile_id,
                                  failed_call_prefix, app_id_err_callback=None):
        if app_id_err_callback is None:
            app_id_err_callback = []
        result = {}
        try:
            apple_obj = AppStoreConnectApi(self.issuer_id, self.private_key_id, self.p8key)
            profile_obj = apple_obj.create_profile(profile_id, developer_app_id, auth.get('cert_id'),
                                                   provision_name.split("/")[-1],
                                                   device_id_list)
            if profile_obj:
                result['profile_id'] = profile_obj.id
                n = base64.b64decode(profile_obj.profileContent)
                if not os.path.isdir(os.path.dirname(provision_name)):
                    os.makedirs(os.path.dirname(provision_name))
                with open(provision_name, 'wb') as f:
                    f.write(n)
                return True, result
        except Exception as e:
            logger.error(f"app_id {app_obj.app_id} ios developer make profile Failed Exception:{e}")
            result['return_info'] = "%s" % e
            if app_id_err_callback and "There is no App ID with ID" in str(e):
                CleanErrorBundleIdSignDataState.set_state(failed_call_prefix)
                for call_fun in app_id_err_callback:
                    call_fun()
                CleanErrorBundleIdSignDataState.del_state(failed_call_prefix)
            return False, result

    def modify_capability(self, app_obj, developer_app_id):
        bundle_id = app_obj.bundle_id
        app_id = app_obj.app_id
        s_type = app_obj.supersign_type
        result = {}
        try:
            apple_obj = AppStoreConnectApi(self.issuer_id, self.private_key_id, self.p8key)
            if developer_app_id:
                if s_type == 0:
                    result['code'] = apple_obj.disable_capability_by_s_type(developer_app_id)
                else:
                    result['code'] = apple_obj.enable_capability_by_s_type(developer_app_id, s_type)
            else:
                if s_type == 0:
                    bundle_obj = apple_obj.register_bundle_id(app_id, f"{bundle_id}.{self.issuer_id}.{app_id}")
                else:
                    bundle_obj = apple_obj.register_bundle_id_enable_capability(app_id,
                                                                                f"{bundle_id}.{self.issuer_id}.{app_id}",
                                                                                s_type)
                developer_app_id = bundle_obj.id
                result['aid'] = developer_app_id
            return True, result
        except Exception as e:
            logger.error("ios developer modify_capability Failed Exception:%s" % e)
            result['return_info'] = "%s" % e
            return False, result

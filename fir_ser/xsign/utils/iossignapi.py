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
import signal
import time
from subprocess import Popen, PIPE

from OpenSSL.crypto import (load_pkcs12, dump_certificate_request, dump_privatekey, PKey, TYPE_RSA, X509Req,
                            dump_certificate, load_privatekey, load_certificate, PKCS12, FILETYPE_PEM, FILETYPE_ASN1)

from common.base.baseutils import get_format_time, format_apple_date, make_app_uuid
from common.cache.state import CleanErrorBundleIdSignDataState
from common.constants import AppleDeveloperStatus
from common.core.sysconfig import Config
from common.libs.apple.appleapiv3 import AppStoreConnectApi, Certificates, Devices, BundleIds, Profiles
from fir_ser.settings import SUPER_SIGN_ROOT
from xsign.models import AppIOSDeveloperInfo
from xsign.utils.modelutils import add_sign_message

logger = logging.getLogger(__name__)


def shell_command(command, timeout):
    result = {'exit_code': 99, 'return_info': ''}
    shell_start_time = time.time()
    child = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
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
    logger.info(f'shell: {command} - return_info:{out} - exit_code:{child.returncode}')
    return result


def exec_shell(cmd, timeout=None):
    logger.info(f"exec_shell cmd:{cmd}")
    result = shell_command(cmd, timeout)
    logger.info(f"exec_shell cmd:{cmd}  result:{result}")
    if result.get("exit_code") != 0:
        err_info = result.get("err_info", result.get("return_info", None))
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
        self.cmd = f"zsign  -c '{self.app_dev_pem}'  -k '{self.my_local_key}' "

    @staticmethod
    def sign_mobile_config(sign_data, ssl_pem_path, ssl_key_path, ssl_pem_data=None, ssl_key_data=None):
        """
        :param ssl_key_data:
        :param ssl_pem_data:
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
            if not ssl_key_data:
                ssl_key_data = open(ssl_key_path, 'rb').read()

            if not ssl_pem_data:
                ssl_pem_data = open(ssl_pem_path, 'rb').read()

            cert_list = re.findall('-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----',
                                   ssl_pem_data.decode('utf-8'), re.S)
            if len(cert_list) == 0:
                raise Exception('load cert failed')
            else:
                cert = x509.load_pem_x509_certificate(cert_list[0].encode('utf-8'))
                cas = [cert]
                if len(cert_list) > 1:
                    cas.extend([x509.load_pem_x509_certificate(x.encode('utf-8')) for x in cert_list[1:]])
                key = serialization.load_pem_private_key(ssl_key_data, None)
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
            properties = f"{properties} {k} '{v}' "
        return exec_shell(f"{self.cmd} {properties} -m '{new_profile}' -o '{new_ipa}' -z 9 '{org_ipa}'")


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


def check_error_call_back(error, developer_pk):
    msg = ''
    status = None
    if 'Cannot connect to proxy' in error or 'Read timed out' in error or 'Max retries exceeded with' in error:
        logger.error('access apple api failed . change proxy ip again')
        msg = "代理网络错误，请稍后重试或联系管理员处理"
    if 'it may be encrypted with an unsupported algorithm' in error:
        msg = "数据校验失败，请检查p8key内容是否正常"
        status = AppleDeveloperStatus.ABNORMAL_STATUS
    if 'Authentication credentials are missing or invalid' in error:
        msg = '认证失败，请检查开发者信息填写是否正确'
        status = AppleDeveloperStatus.ABNORMAL_STATUS
    if 'FORBIDDEN.REQUIRED_AGREEMENTS_MISSING_OR_EXPIRED' in error:
        msg = '请登录 https://developer.apple.com/account/ 并同意最新协议'
        status = AppleDeveloperStatus.AGREEMENT_NOT_AGREED
    if status is not None:
        developer_obj = AppIOSDeveloperInfo.objects.filter(pk=developer_pk).first()
        if developer_obj:
            if developer_obj.status == AppleDeveloperStatus.BAN and status == AppleDeveloperStatus.ABNORMAL_STATUS:
                status = AppleDeveloperStatus.BAN
        AppIOSDeveloperInfo.objects.filter(pk=developer_pk).update(status=status)
    logger.error(f"{msg} {error}")
    return msg if msg else error


class AppDeveloperApiV2(object):
    def __init__(self, issuer_id, private_key_id, p8key, cert_id, developer_pk, app_obj):
        self.issuer_id = issuer_id
        self.private_key_id = private_key_id
        self.p8key = p8key
        self.cert_id = cert_id
        self.developer_pk = developer_pk
        self.app_obj = app_obj

    def __getattribute__(self, name):
        attr = object.__getattribute__(self, name)
        if hasattr(attr, '__call__'):
            def func(*args, **kwargs):
                if attr.__name__ in ['get_developer_cert_info', 'get_device', '__result_format', '__callback_run']:
                    return attr(*args, **kwargs)
                else:
                    if AppIOSDeveloperInfo.objects.filter(pk=self.developer_pk,
                                                          status__in=Config.DEVELOPER_WRITE_STATUS).first():
                        start_time = time.time()
                        logger.info(f'issuer_id:{self.issuer_id}  calling {attr.__name__} time:{start_time}')
                        result = attr(*args, **kwargs)
                        logger.info(
                            f'issuer_id:{self.issuer_id}  done {attr.__name__} used time:{time.time() - start_time}')
                        return result
                    else:
                        result = False, {'return_info': '开发者状态异常'}
                        logger.warning(f'issuer_id:{self.issuer_id}  can not calling {attr.__name__} {result}')
                        return result

            return func
        else:
            return attr

    def __file_format_path_name(self, user_obj):
        cert_dir_name = make_app_uuid(user_obj, self.issuer_id)
        cert_dir_path = os.path.join(SUPER_SIGN_ROOT, cert_dir_name)
        if not os.path.isdir(cert_dir_path):
            os.makedirs(cert_dir_path)
        return os.path.join(cert_dir_path, cert_dir_name)

    def __result_format(self, result, is_instance):
        return_flag = False
        if isinstance(result, list):
            if len(result) == 0:
                return_flag = True
            else:
                if isinstance(result[0], is_instance):
                    return_flag = True
        else:
            if isinstance(result, is_instance):
                result = [result]
                return_flag = True
        if return_flag:
            logger.info(f"issuer_id:{self.issuer_id} {is_instance} result:{result}")
            return True, result
        raise Exception(f'{result} is not {is_instance}')

    def __callback_run(self, err_msg, failed_call_prefix, callback_info=None):
        if callback_info is None:
            callback_info = []
        for callback in callback_info:
            for match_msg in callback.get('err_match_msg', []):
                if match_msg in err_msg:
                    with CleanErrorBundleIdSignDataState(failed_call_prefix) as state:
                        if state:
                            for func in callback.get('func_list', []):
                                msg = f'issuer_id:{self.issuer_id} run callback func {func.__name__}.err_msg:{err_msg}'
                                logger.warning(msg)
                                developer_obj = AppIOSDeveloperInfo.objects.filter(pk=self.developer_pk).first()
                                if developer_obj:
                                    add_sign_message(developer_obj.user_id, developer_obj, self.app_obj,
                                                     '操作失败，执行失败回调方法',
                                                     msg, False)
                                func()
                        else:
                            logger.warning(
                                f'issuer_id:{self.issuer_id} {callback_info}-{failed_call_prefix} is running')

    def get_developer_cert_info(self, query_parameters=None):
        """
        :return:  结果为空列表，或者是 object 或者是 [object,object] 其他为 false
        """
        result = {}
        try:
            apple_obj = AppStoreConnectApi(self.issuer_id, self.private_key_id, self.p8key)
            certificates = apple_obj.get_all_certificates(query_parameters)
            return self.__result_format(certificates, Certificates)
        except Exception as e:
            logger.error(f"issuer_id:{self.issuer_id} ios developer active Failed Exception:{e}")
            result['return_info'] = check_error_call_back(str(e), self.developer_pk)
        return False, result

    def create_cert(self, user_obj):
        result = {}
        try:
            apple_obj = AppStoreConnectApi(self.issuer_id, self.private_key_id, self.p8key)
            csr_path = self.__file_format_path_name(user_obj)
            if not os.path.isdir(os.path.dirname(csr_path)):
                os.makedirs(os.path.dirname(csr_path))
            csr_content = make_csr_content(csr_path + ".csr", csr_path + ".key")
            certificates = apple_obj.create_certificate(csr_content.decode("utf-8"))
            if certificates and isinstance(certificates, Certificates):
                n = base64.b64decode(certificates.certificateContent)
                with open(csr_path + ".cer", 'wb') as f:
                    f.write(n)
                make_pem(n, csr_path + ".pem")
                logger.info(
                    f"issuer_id:{self.issuer_id} ios developer create cert result:{certificates.certificateContent}")
                return True, certificates
            raise Exception(str(certificates))
        except Exception as e:
            logger.error(f"issuer_id:{self.issuer_id} ios developer create cert Failed Exception:{e}")
            result['return_info'] = check_error_call_back(str(e), self.developer_pk)
        return False, result

    def get_cert_obj_by_cid(self):
        result = {}
        try:
            apple_obj = AppStoreConnectApi(self.issuer_id, self.private_key_id, self.p8key)
            cert_obj = apple_obj.get_certificate_by_cid(self.cert_id)
            if cert_obj and isinstance(cert_obj, Certificates):
                return True, cert_obj
            else:
                logger.info(f"issuer_id:{self.issuer_id} ios developer get cert {self.cert_id} failed")
                return False, result
        except Exception as e:
            logger.error(f"issuer_id:{self.issuer_id} ios developer get cert {self.cert_id} Failed Exception:{e}")
            result['return_info'] = check_error_call_back(str(e), self.developer_pk)
        return False, result

    def revoke_cert(self):
        result = {}
        try:
            apple_obj = AppStoreConnectApi(self.issuer_id, self.private_key_id, self.p8key)
            cert_obj = apple_obj.get_certificate_by_cid(self.cert_id)
            if cert_obj and isinstance(cert_obj, Certificates):
                s_date = format_apple_date(cert_obj.expirationDate)
                if s_date.timestamp() - datetime.datetime.now().timestamp() < 3600 * 24 * 3:
                    if apple_obj.revoke_certificate(self.cert_id):
                        logger.info(f"issuer_id:{self.issuer_id} ios developer cert {self.cert_id} revoke")
                        return True, result
                else:
                    logger.info(
                        f"issuer_id:{self.issuer_id} ios developer cert {self.cert_id} not revoke.because expire time < 3 day ")
                    return True, result
            raise Exception(str(cert_obj))
        except Exception as e:
            logger.error(f"issuer_id:{self.issuer_id} ios developer cert {self.cert_id} revoke Failed Exception:{e}")
            result['return_info'] = check_error_call_back(str(e), self.developer_pk)
        return False, result

    def auto_set_certid_by_p12(self, app_dev_pem):
        result = {}
        try:
            cer = load_certificate(FILETYPE_PEM, open(app_dev_pem, 'rb').read())
            not_after = datetime.datetime.strptime(cer.get_notAfter().decode('utf-8'), "%Y%m%d%H%M%SZ")
            apple_obj = AppStoreConnectApi(self.issuer_id, self.private_key_id, self.p8key)
            certificates = apple_obj.get_all_certificates({'filter[certificateType]': 'IOS_DISTRIBUTION'})
            status, result = self.__result_format(certificates, Certificates)
            if status:
                for cert_obj in result:
                    f_date = format_apple_date(cert_obj.expirationDate)
                    logger.info(
                        f"issuer_id:{self.issuer_id} {cert_obj.id}-{not_after.timestamp()} - {f_date.timestamp()} - {cer.get_serial_number()} - {cert_obj.serialNumber} ")
                    # if not_after.timestamp() == f_date.timestamp(): # 比较证书的序列号来判断是否为同一个证书
                    if cer.get_serial_number() == int(cert_obj.serialNumber, 16):
                        return True, cert_obj
            result = {}
            raise Exception(str('证书不匹配，请更换其他开发证书重新导入'))
        except Exception as e:
            logger.error(f"issuer_id:{self.issuer_id} ios developer cert {app_dev_pem} auto get Failed Exception:{e}")
            result['return_info'] = check_error_call_back(str(e), self.developer_pk)
        return False, result

    def del_profile(self, profile_id, profile_name):
        result = {}
        try:
            apple_obj = AppStoreConnectApi(self.issuer_id, self.private_key_id, self.p8key)
            if apple_obj.delete_profile_by_id(profile_id, profile_name):
                return True
        except Exception as e:
            logger.error(f"issuer_id:{self.issuer_id} ios developer delete profile Failed Exception:{e}")
            result['return_info'] = check_error_call_back(str(e), self.developer_pk)
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
            logger.info(f"issuer_id:{self.issuer_id} device_obj:{device_obj} result:{status}")
            if device_obj and isinstance(device_obj, Devices):
                return True, device_obj
            raise Exception(str(device_obj))
        except Exception as e:
            err_msg = str(e)
            logger.error(f"issuer_id:{self.issuer_id} ios developer set devices status Failed Exception:{e}")
            result['return_info'] = check_error_call_back(err_msg, self.developer_pk)
            self.__callback_run(err_msg, failed_call_prefix, device_err_callback)

        return False, result

    def get_device(self):
        result = {}
        try:
            apple_obj = AppStoreConnectApi(self.issuer_id, self.private_key_id, self.p8key)
            devices_obj_list = apple_obj.get_all_devices()
            return self.__result_format(devices_obj_list, Devices)
        except Exception as e:
            logger.error(f"issuer_id:{self.issuer_id} ios developer get device Failed Exception:{e}")
            result['return_info'] = check_error_call_back(str(e), self.developer_pk)
            return False, result

    def del_app(self, identifier_id, bundle_id, app_id):
        result = {}
        try:
            apple_obj = AppStoreConnectApi(self.issuer_id, self.private_key_id, self.p8key)
            if apple_obj.delete_bundle_by_identifier(identifier_id, f"{bundle_id}.{self.issuer_id}.{app_id}"):
                return True, result

        except Exception as e:
            logger.error(f"issuer_id:{self.issuer_id} ios developer delete app Failed Exception:{e}")
            result['return_info'] = check_error_call_back(str(e), self.developer_pk)
            return False, result

    def create_app(self, bundle_id, app_id, s_type, failed_call_prefix, app_id_err_callback=None):
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
            if bundle_obj and isinstance(bundle_obj, BundleIds):
                result['aid'] = bundle_obj.id
                return True, result
            raise Exception(str(bundle_obj))
        except Exception as e:
            err_msg = str(e)
            logger.error(f"issuer_id:{self.issuer_id} ios developer create app Failed Exception:{e}")
            result['return_info'] = check_error_call_back(err_msg, self.developer_pk)
            self.__callback_run(err_msg, failed_call_prefix, app_id_err_callback)
            return False, result

    def register_device(self, device_udid, device_name, failed_call_prefix, device_err_callback=None):
        result = {}
        try:
            apple_obj = AppStoreConnectApi(self.issuer_id, self.private_key_id, self.p8key)
            device_obj = apple_obj.register_device(device_name, device_udid)
            if device_obj and isinstance(device_obj, Devices):
                return True, device_obj
            raise Exception(str(device_obj))
        except Exception as e:
            err_msg = str(e)
            logger.error(f"issuer_id:{self.issuer_id} ios developer register device Failed Exception:{e}")
            result['return_info'] = check_error_call_back(err_msg, self.developer_pk)
            self.__callback_run(err_msg, failed_call_prefix, device_err_callback)
            return False, result

    def make_and_download_profile(self, app_obj, provision_name, auth, developer_app_id, device_id_list, profile_id,
                                  failed_call_prefix, callback_info=None):
        result = {}
        try:
            apple_obj = AppStoreConnectApi(self.issuer_id, self.private_key_id, self.p8key)
            profile_obj = apple_obj.create_profile(profile_id, developer_app_id, auth.get('cert_id'),
                                                   provision_name.split("/")[-1],
                                                   device_id_list)
            if profile_obj and isinstance(profile_obj, Profiles):
                result['profile_id'] = profile_obj.id
                n = base64.b64decode(profile_obj.profileContent)
                if not os.path.isdir(os.path.dirname(provision_name)):
                    os.makedirs(os.path.dirname(provision_name))
                with open(provision_name, 'wb') as f:
                    f.write(n)
                return True, result
            raise Exception(str(profile_obj))
        except Exception as e:
            err_msg = str(e)
            logger.error(f"issuer_id:{self.issuer_id} app_id {app_obj.app_id} ios developer make profile Failed "
                         f"Exception:{e}")
            result['return_info'] = check_error_call_back(err_msg, self.developer_pk)
            self.__callback_run(err_msg, failed_call_prefix, callback_info)
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
                if bundle_obj and isinstance(bundle_obj, BundleIds):
                    developer_app_id = bundle_obj.id
                    result['aid'] = developer_app_id
                else:
                    raise Exception(str(bundle_obj))
            return True, result
        except Exception as e:
            logger.error(f"issuer_id:{self.issuer_id} ios developer modify_capability Failed Exception:{e}")
            result['return_info'] = check_error_call_back(str(e), self.developer_pk)
            return False, result

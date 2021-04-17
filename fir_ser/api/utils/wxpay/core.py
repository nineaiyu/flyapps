# -*- coding: utf-8 -*-
import json
from enum import Enum

import requests

# -*- coding: utf-8 -*-

import time
import uuid
from base64 import b64decode, b64encode
import json

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.serialization import (load_pem_private_key,
                                                          load_pem_public_key)
from OpenSSL import crypto


def build_authorization(path,
                        method,
                        mchid,
                        serial_no,
                        mch_private_key,
                        data=None,
                        nonce_str=None):
    timeStamp = str(int(time.time()))
    nonce_str = nonce_str or ''.join(str(uuid.uuid4()).split('-')).upper()
    body = json.dumps(data) if data else ''
    sign_str = method + '\n' + path + '\n' + \
               timeStamp + '\n' + nonce_str + '\n' + body + '\n'
    signature = sign(private_key=mch_private_key, sign_str=sign_str)
    authorization = 'WECHATPAY2-SHA256-RSA2048 mchid="%s",nonce_str="%s",signature="%s",timestamp="%s",serial_no="%s"' % (
        mchid, nonce_str, signature, timeStamp, serial_no)
    return authorization


def sign(private_key, sign_str):
    private_key = load_pem_private_key(data=format_private_key(
        private_key).encode('UTF-8'), password=None, backend=default_backend())
    message = sign_str.encode('UTF-8')
    signature = private_key.sign(message, PKCS1v15(), SHA256())
    sign = b64encode(signature).decode('UTF-8').replace('\n', '')
    return sign


def decrypt(nonce, ciphertext, associated_data, apiv3_key):
    key_bytes = apiv3_key.encode('UTF-8')
    nonce_bytes = nonce.encode('UTF-8')
    associated_data_bytes = associated_data.encode('UTF-8')
    data = b64decode(ciphertext)
    aesgcm = AESGCM(key_bytes)
    return aesgcm.decrypt(nonce_bytes, data, associated_data_bytes).decode('UTF-8')


def format_private_key(private_key):
    pem_start = '-----BEGIN PRIVATE KEY-----\n'
    pem_end = '\n-----END PRIVATE KEY-----'
    if not private_key.startswith(pem_start):
        private_key = pem_start + private_key
    if not private_key.endswith(pem_end):
        private_key = private_key + pem_end
    return private_key


def format_certificate(certificate):
    pem_start = '-----BEGIN CERTIFICATE-----\n'
    pem_end = '\n-----END CERTIFICATE-----'
    if not certificate.startswith(pem_start):
        certificate = pem_start + certificate
    if not certificate.endswith(pem_end):
        certificate = certificate + pem_end
    return certificate


def verify(timestamp, nonce, body, signature, certificate):
    sign_str = '%s\n%s\n%s\n' % (timestamp, nonce, body)
    public_key_str = dump_public_key(certificate)
    public_key = load_pem_public_key(data=public_key_str.encode('UTF-8'), backend=default_backend())
    message = sign_str.encode('UTF-8')
    signature = b64decode(signature)
    try:
        public_key.verify(signature, sign_str.encode('UTF-8'), PKCS1v15(), SHA256())
    except InvalidSignature:
        return False
    return True


def certificate_serial_number(certificate):
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, format_certificate(certificate))
    try:
        res = cert.get_signature_algorithm().decode('UTF-8')
        if res != 'sha256WithRSAEncryption':
            return None
        return hex(cert.get_serial_number()).upper()[2:]
    except:
        return None


def dump_public_key(certificate):
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, format_certificate(certificate))
    public_key = crypto.dump_publickey(crypto.FILETYPE_PEM, cert.get_pubkey()).decode("utf-8")
    return public_key


class RequestType(Enum):
    GET = 0
    POST = 1


class Core():
    def __init__(self, mchid, cert_serial_no, private_key, apiv3_key):
        self._mchid = mchid
        self._cert_serial_no = cert_serial_no
        self._private_key = private_key
        self._apiv3_key = apiv3_key
        self._gate_way = 'https://api.mch.weixin.qq.com'
        self._certificates = []
        self._update_certificates()

    def _update_certificates(self):
        path = '/v3/certificates'
        code, message = self.request(
            path,
            skip_verify=False if self._certificates else True)
        if code == 200:
            self._certificates.clear()
            data = json.loads(message).get('data')
            for v in data:
                serial_no = v.get('serial_no')
                effective_time = v.get('effective_time')
                expire_time = v.get('expire_time')
                encrypt_certificate = v.get('encrypt_certificate')
                algorithm = nonce = associated_data = ciphertext = None
                if encrypt_certificate:
                    algorithm = encrypt_certificate.get('algorithm')
                    nonce = encrypt_certificate.get('nonce')
                    associated_data = encrypt_certificate.get(
                        'associated_data')
                    ciphertext = encrypt_certificate.get('ciphertext')
                if not (
                        serial_no and effective_time and expire_time and algorithm and nonce and associated_data and ciphertext):
                    continue
                certificate = decrypt(
                    nonce=nonce,
                    ciphertext=ciphertext,
                    associated_data=associated_data,
                    apiv3_key=self._apiv3_key)
                self._certificates.append(certificate)

    def verify_signature(self, headers, body):
        signature = headers.get('Wechatpay-Signature')
        timestamp = headers.get('Wechatpay-Timestamp')
        nonce = headers.get('Wechatpay-Nonce')
        serial_no = headers.get('Wechatpay-Serial')
        verified = False
        for cert in self._certificates:
            if serial_no == certificate_serial_number(cert):
                verified = True
                certificate = cert
                break
        if not verified:
            self._update_certificates()
            for cert in self._certificates:
                if serial_no == certificate_serial_number(cert):
                    verified = True
                    certificate = cert
                    break
            if not verified:
                return False
        if not verify(timestamp, nonce, body, signature, certificate):
            return False
        return True

    def request(self, path, method=RequestType.GET, data=None, skip_verify=False):
        headers = {}
        headers.update({'Content-Type': 'application/json'})
        headers.update({'Accept': 'application/json'})
        headers.update(
            {'User-Agent': 'wechatpay v3 python sdk(https://github.com/minibear2021/wechatpayv3)'})
        authorization = build_authorization(
            path,
            'GET' if method == RequestType.GET else 'POST',
            self._mchid,
            self._cert_serial_no,
            self._private_key,
            data=data)
        headers.update({'Authorization': authorization})
        if method == RequestType.GET:
            response = requests.get(url=self._gate_way + path, headers=headers)
        else:
            response = requests.post(
                self._gate_way + path, json=data, headers=headers)

        if response.status_code in range(200, 300) and not skip_verify:
            if not self.verify_signature(response.headers, response.text):
                raise Exception('failed to verify signature')
        return response.status_code, response.text

    def sign(self, sign_str):
        return sign(self._private_key, sign_str)

    def decrypt_callback(self, headers, body):
        if self.verify_signature(headers, body):
            data = json.loads(body)
            resource_type = data.get('resource_type')
            if resource_type != 'encrypt-resource':
                return None
            resource = data.get('resource')
            if not resource:
                return None
            algorithm = resource.get('algorithm')
            if algorithm != 'AEAD_AES_256_GCM':
                return None
            nonce = resource.get('nonce')
            ciphertext = resource.get('ciphertext')
            associated_data = resource.get('associated_data')
            if not (nonce and ciphertext):
                return None
            if not associated_data:
                associated_data = ''
            result = decrypt(
                nonce=nonce,
                ciphertext=ciphertext,
                associated_data=associated_data,
                apiv3_key=self._apiv3_key)
            return result
        else:
            return None

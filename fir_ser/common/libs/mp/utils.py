#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 9月 
# author: NinEveN
# date: 2021/9/6

import base64
import hashlib
import logging
import random
import socket
import string
import struct
import time
import xml.etree.cElementTree as ET

from Crypto.Cipher import AES

from . import ierror

logger = logging.getLogger(__name__)


class XMLParse:
    """提供提取消息格式中的密文及生成回复消息格式的接口"""

    # xml消息模板
    AES_TEXT_RESPONSE_TEMPLATE = """<xml>
<Encrypt><![CDATA[%(msg_encrypt)s]]></Encrypt>
<MsgSignature><![CDATA[%(msg_signature)s]]></MsgSignature>
<TimeStamp>%(timestamp)s</TimeStamp>
<Nonce><![CDATA[%(nonce)s]]></Nonce>
</xml>"""

    def extract(self, xml_text):
        """提取出xml数据包中的加密消息
        @param xml_text: 待提取的xml字符串
        @return: 提取出的加密消息字符串
        """
        try:
            xml_tree = ET.fromstring(xml_text)
            encrypt = xml_tree.find("Encrypt")
            to_user_name = xml_tree.find("ToUserName")
            return ierror.WXBizMsgCrypt_OK, encrypt.text, to_user_name.text
        except Exception as e:
            logger.error(e)
            return ierror.WXBizMsgCrypt_ParseXml_Error, None, None

    def generate(self, encrypt, signature, timestamp, nonce):
        """生成xml消息
        @param encrypt: 加密后的消息密文
        @param signature: 安全签名
        @param timestamp: 时间戳
        @param nonce: 随机字符串
        @return: 生成的xml字符串
        """
        resp_dict = {
            'msg_encrypt': encrypt,
            'msg_signature': signature,
            'timestamp': timestamp,
            'nonce': nonce,
        }
        resp_xml = self.AES_TEXT_RESPONSE_TEMPLATE % resp_dict
        return resp_xml


class PKCS7Encoder(object):
    """提供基于PKCS7算法的加解密接口"""

    block_size = 32

    def encode(self, text):
        """ 对需要加密的明文进行填充补位
        @param text: 需要进行填充补位操作的明文
        @return: 补齐明文字符串
        """
        text_length = len(text)
        # 计算需要填充的位数
        amount_to_pad = self.block_size - (text_length % self.block_size)
        if amount_to_pad == 0:
            amount_to_pad = self.block_size
        # 获得补位所用的字符
        pad = chr(amount_to_pad)
        return text + pad * amount_to_pad

    def decode(self, decrypted):
        """删除解密后明文的补位字符
        @param decrypted: 解密后的明文
        @return: 删除补位字符后的明文
        """
        pad = ord(decrypted[-1])
        if pad < 1 or pad > 32:
            pad = 0
        return decrypted[:-pad]


def get_random_str():
    """ 随机生成16位字符串
    @return: 16位字符串
    """
    rule = string.ascii_letters + string.digits
    return "".join(random.sample(rule, 16))


class Prpcrypt(object):
    """提供接收和推送给公众平台消息的加解密接口"""

    def __init__(self, key):
        # self.key = base64.b64decode(key+"=")
        self.key = key
        # 设置加解密模式为AES的CBC模式
        self.mode = AES.MODE_CBC

    def encrypt(self, text, app_id):
        """对明文进行加密
        :param text: 需要加密的明文
        :param app_id: 应用id
        @return: 加密得到的字符串
        """
        # 16位随机字符串添加到明文开头
        text = get_random_str() + struct.pack("I", socket.htonl(len(text))).decode('utf-8') + text + app_id
        # 使用自定义的填充方式对明文进行补位填充
        pkcs7 = PKCS7Encoder()
        text = pkcs7.encode(text)
        # 加密
        crypto = AES.new(self.key, self.mode, self.key[:16])
        try:
            ciphertext = crypto.encrypt(text)
            # 使用BASE64对加密后的字符串进行编码
            return ierror.WXBizMsgCrypt_OK, base64.b64encode(ciphertext)
        except Exception as e:
            logger.error(e)
            return ierror.WXBizMsgCrypt_EncryptAES_Error, None

    def decrypt(self, text, app_id):
        """ 对解密后的明文进行补位删除
        :param text: 密文
        :param app_id: 应用id
        :return: 删除填充补位后的明文
        """
        try:
            cryptor = AES.new(self.key, self.mode, self.key[:16])
            # 使用BASE64对密文进行解码，然后AES-CBC解密
            plain_text = cryptor.decrypt(base64.b64decode(text))
        except Exception as e:
            logger.error(e)
            return ierror.WXBizMsgCrypt_DecryptAES_Error, None
        try:
            pad = plain_text[-1]
            # 去掉补位字符串
            # pkcs7 = PKCS7Encoder()
            # plain_text = pkcs7.encode(plain_text)
            # 去除16位随机字符串
            content = plain_text[16:-pad]
            xml_len = socket.ntohl(struct.unpack("I", content[: 4])[0])
            xml_content = content[4: xml_len + 4]
            from_app_id = content[xml_len + 4:].decode('utf-8')
        except Exception as e:
            logger.error(e)
            return ierror.WXBizMsgCrypt_IllegalBuffer, None
        if from_app_id != app_id:
            return ierror.WXBizMsgCrypt_ValidateAppid_Error, None
        return 0, xml_content


class WxMsgCryptBase(object):
    def __init__(self, app_id, app_secret, token, encoding_aes_key):
        try:
            self.key = base64.b64decode(encoding_aes_key + "=")
            assert len(self.key) == 32
        except Exception as e:
            logger.error(f"{encoding_aes_key} 解密失败 Exception:{e}")
            raise Exception("[error]: EncodingAESKey invalid !")
        self.token = token
        self.app_id = app_id

    def encrypt_msg(self, msg, nonce, timestamp=None):
        """
        :param msg: 企业号待回复用户的消息，xml格式的字符串
        :param nonce: 随机串，可以自己生成，也可以用URL参数的nonce
        :param timestamp: 时间戳，可以自己生成，也可以用URL参数的timestamp,如为None则自动用当前时间
        :return: 成功0，sEncryptMsg,失败返回对应的错误码None
        """
        pc = Prpcrypt(self.key)
        ret, encrypt = pc.encrypt(msg, self.app_id)
        if ret != 0:
            return ret, None
        if timestamp is None:
            timestamp = str(int(time.time()))

        try:
            sha = hashlib.sha1(("".join(sorted([self.token, timestamp, nonce, encrypt]))).encode('utf-8'))
            return ret, XMLParse().generate(encrypt, sha.hexdigest(), timestamp, nonce)
        except Exception as e:
            logger.error(e)
            return ierror.WXBizMsgCrypt_ComputeSignature_Error, None

    def decrypt_msg(self, msg, msg_signature, timestamp, nonce):
        """
        :param msg: 密文，对应POST请求的数据
        :param msg_signature:  签名串，对应URL参数的msg_signature
        :param timestamp: 时间戳，对应URL参数的timestamp
        :param nonce: 随机串，对应URL参数的nonce
        :return: 成功0，失败返回对应的错误码
        """

        if isinstance(msg, str):
            ret, encrypt, _ = XMLParse().extract(msg)
            if ret != 0:
                return ret, None
        else:
            encrypt = msg.get('Encrypt')
        try:
            sha = hashlib.sha1(("".join(sorted([self.token, timestamp, nonce, encrypt]))).encode('utf-8'))
            if not sha.hexdigest() == msg_signature:
                return ierror.WXBizMsgCrypt_ValidateSignature_Error, None
            pc = Prpcrypt(self.key)
            ret, xml_content = pc.decrypt(encrypt, self.app_id)
            return ret, xml_content
        except Exception as e:
            logger.error(e)
            return ierror.WXBizMsgCrypt_ComputeSignature_Error, None

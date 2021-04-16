#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月 
# author: NinEveN
# date: 2021/4/15

import time
import random
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import pkcs1_15
from Cryptodome.Hash import SHA256
from base64 import b64encode

mchid = '1608486112'
app_id = 'wx390e5985fd3699e6'
serial_no = '27DADA4D2921CDD66B8B20A68276F09B90754922'
private_key = '''-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDbXhNoHljrkS8T
jXg3+tTkaoOol8FDt0jSGckhzX46gkS16CWYwTthBKurfFtynsJe4uDOphS1ge/r
QEU3+rWNxqa8o6gHSpp2UTYAz/1oYOlXuSa4NA1uD47lmVZJzad2ybWDSsoeRjFj
c+X6F0ZiE3FmdN1iHz8NmbP99foih4smv15X+wX5DrsuLuPVHNB4D0fqvY7P5PO3
wUQXWQNezCYzpPoXX2H/UkyFEFZhWk6/9z3aAkYmqfd6IWPHewOqnVoQRKmo5bXb
yWbB+QIl/HcSfNtq869s5lLGR2Rl2UX8IFXCcXnRPhSAVIeWfXN26Pc9dz9N4VTU
yiZ8Y6AHAgMBAAECggEABdS0U1orJufPBogGIAbMzd1+7mZKPtCKYPtKe1mI92kr
BmLLTQol1+hV39MIYz2RERCaxSNo/YIcrHYi4OALH1+eYvk+qCL1hBuYgeEFbVbW
HPzQ6KiJitljBPtUbdXHk8K8zmaYhMF84pXcEQ+5UTYPF5gXoloORQBG5oM5SN2g
2GTgYw1cpDzzRRwnmpvYd1ZydYNj8m6k7I2L1pwzRS/6/whz1sScpfh+91w1IVM0
WT+pPSdiVtQ7ktmvcTrWj7eNIbcsptZ1QgSV3UHkU0xzLG9N1TqJdHOquunXRS7V
iw/4NgXveXSTSQrmmZVS+Kdyc+z1iDqwOXmE7hjioQKBgQD7js+40NCAPLYXEfer
UFvZ6kem9mJIzAUdeTdK4BjYJrcU+UsXRmcWJIPI9HWSr31f/fSfu2SKyBa6+dFF
SeNHuHPPqQAXrsNuhFG1wcKoNybk7KrsQlXheK7br42565Tegz3UXOKMrnPPlukH
ZZdlYmwBFjEJvIr9jxJvJoW6qQKBgQDfPb697vR8ruLaecPmsq920iC3AQRanYFK
dW6U98JkCN9A/LXA1jGyDTEhtlja+5Ylp0M1EnlcZ079Jnvek5haSNnD0xb1nMy8
P/o0/eWWArTgfjfiJeq1tSdrinGhNz0+Vty74wnbS+5P18H23I5jBlGX5hyNkU4L
axUfJM9jLwKBgCo/1xVkRNB04eRICT/FlFeqKHSbRvCRC37iv+2ca6/J+M/V+s2i
7mdipJuYqzKCtNztayt0rrM8Xczzbjlj6n8+NH05FiHkIUCriomrTEUyVh72vNJH
ZeMjgMK23mfOcEda5YSIQSh9mEfSQbsTTfUiLZ+VGZFYEEP7xo3Se31ZAoGBAJas
LPYytq8EtrYwowktJwJydoQt2otybRYdRmKjCn/MASrypZWeu/Hpt3SCh1xdnAyT
5OeILYMxcv2noMksIxMkwl3KNl/V0dVo9O4ZQ4DJGN3AMuWfI9g6iX2q9mCSUPKn
W9owNbHegN1AyXhdinjJhf6Y4EKohN1uC9Z2WMcfAoGAW90Z2LkqG2fen+R62syP
aaInnu9bitb9rVENCNGXQHdWmIYBMM5zrg8nX8xNJ+yeGQhgxE+YeSq4FOpe0JkA
daWIhg++OHN2MBRutj7oL/AFAxyu467YA5+itEJLHNATbOr/s13S66nePNXox/hr
bIX1aWjPxirQX9mzaL3oEQI=
-----END PRIVATE KEY-----'''
timestamp = str(int(time.time()))
import uuid

wx_public_key = '''

'''


def get_nonce_str():
    """
    获取随机字符串
    :return:
    """
    return str(uuid.uuid4()).replace('-', '')


nonce_str = get_nonce_str()


def sign_str(method, url_path, request_body):
    """
    生成欲签名字符串
    """
    sign_list = [
        method,
        url_path,
        timestamp,
        nonce_str,
        request_body
    ]
    return '\n'.join(sign_list) + '\n'

def sign_response_str(timestamp,nonce_str,request_body):
    """
    生成欲签名字符串
    """
    sign_list = [
        timestamp,
        nonce_str,
        request_body
    ]
    return '\n'.join(sign_list) + '\n'

def sign(sign_str):
    """
    生成签名
    """
    rsa_key = RSA.importKey(private_key)
    signer = pkcs1_15.new(rsa_key)
    digest = SHA256.new(sign_str.encode('utf8'))
    sign = b64encode(signer.sign(digest)).decode('utf8')
    return sign


def authorization(method, url_path, request_body):
    """
    生成Authorization
    """
    str = ""
    if isinstance(request_body, dict):
        str = json.dumps(request_body)
    signstr = sign_str(method, url_path, str)
    s = sign(signstr)
    authorization = 'WECHATPAY2-SHA256-RSA2048  ' \
                    'mchid="{mchid}",' \
                    'nonce_str="{nonce_str}",' \
                    'signature="{sign}",' \
                    'timestamp="{timestamp}",' \
                    'serial_no="{serial_no}"'. \
        format(mchid=mchid,
               nonce_str=nonce_str,
               sign=s,
               timestamp=timestamp,
               serial_no=serial_no
               )
    return authorization


from datetime import timezone

import json

post_data = {
    'appid': app_id,  # 小程序ID
    'mchid': mchid,  # 商户号
    'description': '向 FLY分发平台 充值',  # 商品描述
    'out_trade_no': '12021415113114521722839155',  # 商户订单号
    # 'time_expire': pay_data.get('time_expire'),  # 交易结束时间 示例值：2018-06-08T10:34:56+08:00
    'attach': json.dumps({'user_id': 11}),  # 附加数据，在查询API和支付通知中原样返回，可作为自定义参数使用
    'notify_url': 'https://app.hehelucky.cn/api/v1/fir/server/pay_success',  # 通知地址
    'amount': {
        'total': 10,  # 订单总金额，单位为分。示例值：100
        'currency': 'CNY'
    }
}


def make_pay_pc():
    auth = authorization('POST', '/v3/pay/transactions/native', post_data)
    print(auth)
    import requests
    headers = {
        'Authorization': auth
    }
    req = requests.post('https://api.mch.weixin.qq.com/v3/pay/transactions/native', json=post_data, headers=headers)

    print(req.text)
    print(req.status_code)


def get_wx_cert():
    auth = authorization('GET', '/v3/certificates', '')
    print(auth)
    import requests
    headers = {
        'Authorization': auth
    }
    req = requests.get('https://api.mch.weixin.qq.com/v3/certificates', headers=headers)

    print(req.text)
    print(req.status_code)


from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64

cert_info = {"data": [{"effective_time": "2021-04-15T14:08:03+08:00",
                       "encrypt_certificate": {"algorithm": "AEAD_AES_256_GCM", "associated_data": "certificate",
                                               "ciphertext": "sOuR8QHOOh0QkLBtrsFdrsY6FohdN7JcI6saS7pb/YNowyLlzRQIFmge7C3dILt5DVJu8kzB7dPbqcQmP/J8INSyUqZtFOVVifszWulVyQo23vvC6kT9tHHp/IoPog/Z15rmpyWwmjtrNeWIWILHmmdeSruZKgop4C9L50vQoTBRS3z6JyrACX4OceYwgNR3ICZAu/TNofI6dp92vI9RwIylQxsV1dnzi+m9pYl9IvbF/OGzJazyBPurynFcdcHfq6G7BfKnlmGswh4u5uBqXBoSfzjF14T0clN+sLiZePL0wfyxVRNtAPFkFvsbtiy4ABIbkzwI7T+1Ne/RnLZizpq/4igkILfbtSzBEWO+KRSq2E3ejfKULMZA0uHe0NBVpaAf8f9jR3Bw/16c28hnxidJ+sjf/GMlhm+F3WgzrB7GRuDL97BTdjBKHV5Hm3Q/f94HUrZCUtmoMSihde/I2IE8bI0IPgnuFlOYGZm46yuXtj2aZcr2l9HaT8xCeNnUCPKzY3arVcVZKygKjnTu8Tyvsk4qV54SZTsiQ+hdQohim154401VnP7A2UsKvYQn14xvONkk3POwehe6SJrVwnjlODrKn9qdb2bo0w0yPyV8GkVqi3nn7Eh+Hnq1g6bJb0HXDOpkuf0JF/W0dceMBcTvFTvE0SDAsJgqoIVV1+B4nTCAEbTzmJ5mQKJFL2zzoSXxUZ9ORtWDNzq0Eo0mMnYuivm2fR2IvrjCYAxSXH9X54SmGiENg9usLLfmkp5l0wJqQ29PLB1LEbxI2YonOm0babMd8qfk2d3DVNhm/Uk6uqA+Trk8OtmCTHD6Yt7J4Iz4bqmL4q/1ea2FTIARkg3a+QKj2Yt2tDZeaBHeAsS9et8U82GdP0MQF61OTFhq/NknhyfGUXA6r4lgDN+tmZJyWGkwRhNphXqU6C57JWl8jU2CydPfmTORSlKTScr0fbAYsZQees0TnqnhAYAUFRNsGjdtmQ4fHQDSvXr9ner+e4bsQTqAXzGUYDwtgEjDh26Bn8jpHTkzfC9s491XIHKD5AueNv62JlM4fIDrqJ9o6q2a/skL2EWlegCWWena0eUh+fQdMYzuYg4VAmttk6fwr5S9h15PhyKcPugDyKuXjd3TGVF6oN+pGlyksDUJqrYYvcx16yNdpM4n+B+gf8uCXHpnRd6Ws/g37B0JZUdlIbx6BnXCVGzb8JTHkUOY6ZTQ0ArRn169Ta2DVPUmTIrxID7SZsvYiWiuKywXKfgCdEo3pBPZNthrtBp5GMsJg5dhjsFxsT28FSKolJRfxXViuEs36ybaI9Ks2g6rnBQ8AlpaV6RzWzR8QtTsF481rFK5mC/eaYXFGOGnNmyp12B4ER5UfEm88BBf4xiqk9ZZu8yem7EsomLrovPbF4szYSVyHY2SYalYyjKDZFdH21YUE9lvgQLsBt8LWfOG8PABuUQpEc3a/zVv5F5h+U/oHcdWGirOCIUgI+hk579hpiIdMpOO5YhSrpouuCqX8D+nYpkSbndBGQycfxlTtL2dx0f5DwKqHIPSsKd79F0tqKqodQuRm00KCuqINDNM6TcEwvN8liXy5mgHEbBtWGYlmg6a0Iufy3PvgJkB4hR/gqkEswp7YIJqR2BYoPWLVSROq+d8ExMNHPjihrFRaHDvUecKso7F8Sfq6N6VhScYM6QPk9ow+shc2nsbU+wBl3kHsgaYras+ku+5iHWT8QQk6vWG+RFrfiGfOFzJTXBslt/45ZUc5EdaSUOz9JK+3q8twIl0EBmUM8uThT3uM31/ShdH2ROYz5mdYANERt/23fXOzY4brQJ1gGJ+2wlqKPG/IBemT+1m6z3fGdvPvoQFk02OYmLYIoR0cNa5Y3/MUkGysggflg==",
                                               "nonce": "1ef9f91582da"}, "expire_time": "2026-04-14T14:08:03+08:00",
                       "serial_no": "5091F0B7E805ACD1EDB2A3B7DD04B3A67D177F37"}]}


def decrypt_cert(nonce, ciphertext, associated_data):
    key = "60DbP621a9C3162dDd4AB9c2O15a005L"

    key_bytes = str.encode(key)
    nonce_bytes = str.encode(nonce)
    ad_bytes = str.encode(associated_data)
    data = base64.b64decode(ciphertext)

    aesgcm = AESGCM(key_bytes)
    return aesgcm.decrypt(nonce_bytes, data, ad_bytes)

# encrypt_certificate = cert_info['data'][0]['encrypt_certificate']
# a=decrypt_cert(encrypt_certificate['nonce'],encrypt_certificate['ciphertext'],encrypt_certificate['associated_data'])
# print(a)
# #
# make_pay_pc()

request_body={'id': '65cce1b4-bbb7-541c-b063-5f284f650196', 'create_time': '2021-04-16T18:12:19+08:00', 'resource_type': 'encrypt-resource', 'event_type': 'TRANSACTION.SUCCESS', 'summary': '支付成功', 'resource': {'original_type': 'transaction', 'algorithm': 'AEAD_AES_256_GCM', 'ciphertext': 'rx9sLCTnnrS3GH/WqSMr+eEJqBFNo75Lb9ZW1EnoOhJ/tbJhXYl3biIR+tj1OK7qhj6ctRFeDc/zwwZ9Y5gPuWMADHd7KhsGmFdhJj4ap+UNq6UFO8g2tF3mGRQ11Cj2BCj0F+31EF8n9UCjm9SE1f0vOSwZFM6tx3/pkEgWyBbHqienr2eWZVlv8qlmUqioYoZNdJbfGNLfD/Uo2OqJg2EtXeEmdglrcC6b5hTuqGD/NcBrj83OvgsaimEbtzhphTGWRWKw2/qJtLVGKTHTMFrJ7g990i6w35vEKALWbAKsDIpCtIwPxYXlxtfxMZsLI/CYLN3Oa0W0DeR7GF+TBYgFsbvMAeryq9plbQm50qMDLfuhXcxIc7XutWGREMAmoS8e8NFtMhhi39QA4BVxSiQvND7qPXQBEESAVL+VDyCDN/SlEU2bEu+E6XD1o5LL/hvOlBnXFtm7mXbKj4j2M1II9De2oYD5R25EOXUi5oB24opaPXgHubSr6QpApQrWl3DGVMsaHVsaB4tWHH8XRaJXZpdDjxzz9DtmmTu7ZCBQifWqmC5vb+78f2+9gEavkHbL4XisKf/IFGUxzW3bKi/042xHVB2Z/JM49+Y=', 'associated_data': 'transaction', 'nonce': 'BFK77WOGPp21'}}

wx_headers = {
    'HTTP_WECHATPAY_NONCE': 's6pY4nneUbgFh9nJNiSYv1h9ZLC7ruSj',
    'HTTP_WECHATPAY_SERIAL': '5091F0B7E805ACD1EDB2A3B7DD04B3A67D177F37',
    'HTTP_WECHATPAY_SIGNATURE': 'T8oiVc5oFsEfNDpOSdTeTiVPyO6rbx9MDEV24EtB4myPZhVYmSsJWBrtPXbYemaEPFJTtkrlzGsc3Rm6PsZoOnxSvKVIbvy60So6y36nRSmgawolTK8ruRorm0qaeRJtUAAsJImmQrMlXSqy5YaZqW3GbbLci4r2UYYoDfaNwSTJiwgit3HFYiIL6rYrtUJ3ekwMW5oyT4Aio37ulGnxymC6Nnyqbos4zpo9y6Nc8upf8rStUJ5ya3d+rZxG6fsPkUOVNz9NwaaKQk2YdelpHjd8K/cfaVNJ1ot82x8ArbEWd0k/Iz02LtLLelfF1V0w//0zmukWxWaCV2K9I+ir6w==',
    'HTTP_WECHATPAY_TIMESTAMP': '1618567939',
}
HTTP_WECHATPAY_TIMESTAMP = wx_headers.get('HTTP_WECHATPAY_TIMESTAMP','')
HTTP_WECHATPAY_NONCE = wx_headers.get('HTTP_WECHATPAY_NONCE','')
HTTP_WECHATPAY_SIGNATURE = wx_headers.get('HTTP_WECHATPAY_SIGNATURE','')

WX_CERT_KEY=b'-----BEGIN CERTIFICATE-----\nMIID3DCCAsSgAwIBAgIUUJHwt+gFrNHtsqO33QSzpn0XfzcwDQYJKoZIhvcNAQEL\nBQAwXjELMAkGA1UEBhMCQ04xEzARBgNVBAoTClRlbnBheS5jb20xHTAbBgNVBAsT\nFFRlbnBheS5jb20gQ0EgQ2VudGVyMRswGQYDVQQDExJUZW5wYXkuY29tIFJvb3Qg\nQ0EwHhcNMjEwNDE1MDYwODAzWhcNMjYwNDE0MDYwODAzWjBuMRgwFgYDVQQDDA9U\nZW5wYXkuY29tIHNpZ24xEzARBgNVBAoMClRlbnBheS5jb20xHTAbBgNVBAsMFFRl\nbnBheS5jb20gQ0EgQ2VudGVyMQswCQYDVQQGDAJDTjERMA8GA1UEBwwIU2hlblpo\nZW4wggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDONPXG4eQktFWEVbzD\n7ev8eMK9EEL4BBMCcvQCn76PF3wgbvYSO2CLpp7qP1NNJhFDp5ItUOtvz68AD6u1\nPNWxkOMJqdWPXRpewdUo5nr8lZCR4i3XiY+OSO/cA8C8K8mDvVNsMT1wPMp75Vil\nBL2gK5lfjj/Kjoi/aJSU//gQDpuZ+4GHBFQcOK4QqmPY8rdqhX6z93cFEkFDGPUw\nLXE9jZvYGGf5xwKPFKLvjrrg8zX+znJOXOPQtpvKD/RBfHI9ebv/PxepiHw3prM9\nLoIf6FsVaqFqV1tTJZjAgPAgEhRqM53+8PxZTdxJZDCWv/vf4BvG3Bcfw0CSTlYO\npQpJAgMBAAGjgYEwfzAJBgNVHRMEAjAAMAsGA1UdDwQEAwIE8DBlBgNVHR8EXjBc\nMFqgWKBWhlRodHRwOi8vZXZjYS5pdHJ1cy5jb20uY24vcHVibGljL2l0cnVzY3Js\nP0NBPTFCRDQyMjBFNTBEQkMwNEIwNkFEMzk3NTQ5ODQ2QzAxQzNFOEVCRDIwDQYJ\nKoZIhvcNAQELBQADggEBAA508oXmLC0x0VdsW0ThOeN+BXzuqLsKec945BZz0qPm\n/fc3Wn2Ro5yb5tsh94aqyJGmOWgZsWo/nQk2XcE5BPLn7rX0q7uMGCMbJbxfFiuS\nNuJNDSXamYUCGRXgEsZn8mh8EwZ7MKefq2LxtX9VvJF3o1KsvOWaltr5Ra3DBh1F\nghxzyOOimiqn+duT9ZbbA0nfGJjSsLq61rzc/qBMuBsdJnqeYMFs/+AIDuGYNbOj\nFTcK0+fEFfU1H99RGCu4j9jQlOqnB6uXOnr7VSQPfMEpKd6xTmaa01YHWu9oAijO\nupWVgJZI0cC3/L5s5OzlUp8Bc84NOFxSN0yXAZtH1Bc=\n-----END CERTIFICATE-----'

rsa_key = RSA.importKey(WX_CERT_KEY)
public_key=rsa_key.publickey().exportKey()

Wechatpay_Signature = base64.b64decode(HTTP_WECHATPAY_SIGNATURE)

res_sign_str = sign_response_str(HTTP_WECHATPAY_TIMESTAMP,HTTP_WECHATPAY_NONCE,json.dumps(request_body))
print(res_sign_str)
print(Wechatpay_Signature)

key = RSA.importKey(public_key)

# 验证签名
verifer = pkcs1_15.new(key) # 使用公钥创建校验对象

hasher = SHA256.new(Wechatpay_Signature)# 对收到的消息文本提取摘要
#hasher.update(message.encode())

verifer.verify(hasher, res_sign_str.encode("utf-8")) # 校验摘要（本来的样子）和收到并解密的签名是否一致


# rsa_key = RSA.importKey(private_key)
# signer = pkcs1_15.new(rsa_key)
# digest = SHA256.new(sign_str.encode('utf8'))
# sign = b64encode(signer.sign(digest)).decode('utf8')
#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 7月 
# author: NinEveN
# date: 2021/7/19
import os

from common.constants import AppleDeveloperStatus

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class DOMAINCONF(object):
    API_DOMAIN = "https://app.hehelucky.cn"
    WEB_DOMAIN = "https://app.hehelucky.cn"
    MOBILEPROVISION = "https://static.flyapps.top/embedded2.mobileprovision"


class BASECONF(object):
    VERSION = '1.3.1'

    DEBUG = True

    SECRET_KEY = 'j!g@^bc(z(a3*i&kp$_@bgb)bug&^#3=amch!3lz&1x&s6ss6t'

    ALLOWED_HOSTS = ['127.0.0.1', 'synchrotron', '172.16.133.34', 'ali.cdn.flyapp.dvcloud.xin',
                     'api.src.flyapp.dvcloud.xin', 'app.hehelucky.cn']

    # When Django start it will bind this host and port
    # ./manage.py runserver 127.0.0.1:8080
    # uwsgi运行时绑定端口
    SERVER_BIND_HOST = '127.0.0.1'
    SERVER_LISTEN_PORT = 8898

    # celery flower 任务监控配置
    CELERY_FLOWER_PORT = 5566
    CELERY_FLOWER_HOST = '127.0.0.1'

    # geetest 配置信息
    GEETEST_ID = "d3f3cf73200a70bd3a0c32ea22e5003a"
    GEETEST_KEY = "6f4ab6185c230a4b1f8430f28ebe4804"
    GEETEST_CYCLE_TIME = 10
    GEETEST_BYPASS_STATUS_KEY = "gt_server_bypass_status"
    GEETEST_BYPASS_URL = "https://bypass.geetest.com/v1/bypass_status.php"

    # 访问速率限制
    DEFAULT_THROTTLE_RATES = {
        'ShortAccessUser1': '180/m',
        'ShortAccessUser2': '2000/h',
        'LoginUser': '200/m',
        'RegisterUser1': '40/m',
        'RegisterUser2': '300/h',
        'GetAuthC1': '60/m',
        'GetAuthC2': '300/h',
        'InstallAccess1': '10/m',
        'InstallAccess2': '20/h',
        'ReceiveUdid1': '20/h',
        'ReceiveUdid2': '30/h',
    }


class DBCONF(object):
    host = '127.0.0.1'
    port = '3306'
    password = 'KGzKjZpWBp4R4RSa'
    user = 'flyuser'
    name = 'flyappnew'


class CACHECONF(object):
    host = '127.0.0.1'
    port = '6379'
    password = ''


# 微信公众号登录配置
class THIRDLOGINCONF(object):
    wx_official = {
        'name': 'wx_official',
        'auth': {
            'app_id': '1wx390e5985fd3699e6',
            'app_secret': '5b1796722172a902d019f43e4a2fb678',
            'token': 'f0ae76c1559cacf72a99db6a41b879b8',
            'encoding_aes_key': '7b9U60tCXk3f4yOFideTN5ithh4Y8X3Xl9pRovp83gG',
        },
        'active': False
    }
    wx_applet = {
        'auth': {
            'app_id': 'wxb65d1894331e9ff3',
            'app_secret': 'e05b319562b3b123ffef1d9ce64dd665',
        },
        'active': True
    }


class AUTHCONF(object):
    # 注册方式，如果启用sms或者email 需要配置 THIRD_PART_CONFIG_KEY_INFO.sender 信息
    REGISTER = {
        "enable": True,
        "captcha": False,  # 是否开启注册字母验证码
        "geetest": True,  # 是否开启geetest验证，如要开启请先配置geetest
        "register_type": {
            'sms': True,  # 短信注册
            'email': True,  # 邮件注册
            'code': False,  # 邀请码注册,邀请码必填写，需要和短信，邮件一起使用
        }
    }
    # 个人资料修改修改也会使用该配置
    CHANGER = {
        "enable": True,
        "captcha": False,  # 是否开启注册字母验证码
        "geetest": True,  # 是否开启geetest验证，如要开启请先配置geetest
        "change_type": {
            'sms': True,  # 短信注册
            'email': True,  # 邮件注册
            'code': False,  # 邀请码注册,邀请码必填写，需要和短信，邮件一起使用
        }
    }
    LOGIN = {
        "captcha": False,  # 是否开启登录字母验证码
        "geetest": True,  # 是否开启geetest验证
        "login_type": {
            'sms': True,  # 短信登录
            'email': True,  # 邮件登录
            'up': False,  # 密码登录
            'third': {
                'wxp': THIRDLOGINCONF.wx_official.get('active')  # 微信公众号登录，需要在 THIRDLOGINCONF 配置好微信公众号登录
            },
        }
    }
    REPORT = {
        "enable": True,
        "captcha": False,  # 是否开启注册字母验证码
        "geetest": True,  # 是否开启geetest验证，如要开启请先配置geetest
        "report_type": {
            'sms': False,  # 短信举报
            'email': True,  # 邮件举报
        }
    }
    NOTIFY = {
        "enable": True,
        "captcha": False,  # 是否开启注册字母验证码
        "geetest": True,  # 是否开启geetest验证，如要开启请先配置geetest
        "notify_type": {
            'sms': False,  # 短信通知
            'email': True,  # 邮件通知
            'weixin': True,  # 微信通知
        }
    }


class STORAGEKEYCONF(object):
    STORAGE = [
        {
            'name': 'local',
            'type': 0,
            'auth': {
                'domain_name': DOMAINCONF.API_DOMAIN.split("://")[1],
                # 正式环境需要填写正式的访问域名,如果配置cdn，可以填写cdn的域名，仅支持阿里云 cdn,
                # 开启cdn之后，如果该域名和服务器域名不相同，需要设置阿里云cdn 缓存配置，自定义HTTP响应头 添加 Access-Control-Allow-Origin * 才可以
                'is_https': True if DOMAINCONF.API_DOMAIN.split("://")[0] == "https" else False,
                'download_auth_type': 1,  # 0:不开启token 1:本地token 2:cdn 开启cdn，并且使用本地存储，使用阿里云cdn进行url鉴权，
                'cnd_auth_key': '',  # 当cdn为阿里云并且 download_auth_type=2 的时候 生效,需要 开启阿里云OSS私有Bucket回源
            },
            'active': True
        },
        {
            'name': 'aliyun',
            'type': 2,
            'auth': {
                'access_key': 'LTAI4FkbTR',
                'secret_key': '2iLIxy9',
                'bucket_name': 'fge',
                'sts_role_arn': 'ap-sage',
                'endpoint': 'oss-cn-beijing-internal.aliyuncs.com',  # 服务器和oss在同一个地区，填写内网的endpoint
                'is_https': True,
                'domain_name': 'aoud.xin',
                'download_auth_type': 1,  # 1:oss 2:cdn
                'cnd_auth_key': '',  # 当cdn为阿里云并且 download_auth_type=2 的时候 生效,需要 开启阿里云OSS私有Bucket回源
            },
            'active': False
        },
        {
            'name': 'qiniuyun',
            'type': 1,
            'auth': {
                'access_key': 'mT4fiJ',
                'secret_key': '0G9fXfhYLynv',
                'bucket_name': 'fge',
                'is_https': False,
                'domain_name': 'foud.xin'
            },
            'active': False
        }
    ]


class SENDERCONF(object):
    WHITE_SENDER_CODE = '666666'  # 白名单下，默认不发送真正验证码
    WHITE_SENDER_LIST = [
        '17600102953'
    ]
    SENDER = [
        {
            'name': 'email',
            'type': 0,
            'auth': {
                'email_host': 'smtp.126.com',
                'email_port': 465,
                'use_tls': False,
                'use_ssl': True,
                'username': 'flyapps@126.com',
                'password': 'GGHFEUMZBRZIFZGQ',
                'form': 'fly分发平台 <flyapps@126.com>',
                'subject': '%(code)s验证',
                'template_code': {
                    'login': 'common.libs.sendmsg.template_content.get_userinfo_login_code_html_content',
                    'change': 'common.libs.sendmsg.template_content.get_userinfo_change_code_html_content',
                    'register': 'common.libs.sendmsg.template_content.get_userinfo_register_code_html_content',
                    'password': 'common.libs.sendmsg.template_content.get_userinfo_reset_pwd_html_content',
                    'common': 'common.libs.sendmsg.template_content.get_code_notify_html_content'
                }
            },
            'active': True
        },
        {
            'name': 'aliyun',
            'type': 1,
            'auth': {
                'access_key': 'LTAI5tJH2EnjVzJGMmNCYo9U',
                'secret_key': 'd0LETks5oxkdfbkLGtFihklWGbokab',
                'region_id': 'cn-hangzhou',
                'sing_name': '东城飞阳',
                'template_code': {
                    'login': 'SMS_216700569',
                    'change': 'SMS_216700566',
                    'register': 'SMS_216700567',
                    'password': 'SMS_222341718',
                    'common': 'SMS_227259072'
                }
            },
            'active': True
        },
        {
            'name': 'jiguang',
            'type': 2,
            'auth': {
                'app_key': '93e1a9f71db4f044de4db34a',
                'master_secret': '5f996ee39c7eb52906510cc2',
                'sign_id': '18138',
                'template_code': {
                    'login': '1',
                    'change': '1',
                    'register': '1',
                    'password': '1',
                    'common': '1',
                }
            },
            'active': False
        },
    ]


class IPACONF(object):
    APPLE_DEVELOPER_API_PROXY_LIST = [
        {'proxy': '39.101.198.124:17897', 'active': True},
        {'proxy': '8.142.38.157:17897', 'active': True},
        {'proxy': '121.89.194.26:17897', 'active': True},
        {'proxy': '39.103.139.122:17897', 'active': True},
        {'proxy': '8.142.99.245:17897', 'active': True},
        {'proxy': '8.142.174.13:17897', 'active': True},
        {'proxy': '39.99.238.93:17897', 'active': True},
        {'proxy': '8.142.173.96:17897', 'active': True},
        {'proxy': '8.142.163.150:17897', 'active': True},
        {'proxy': '39.99.148.6:17897', 'active': True},
        {'proxy': '8.142.177.18:17897', 'active': True},
        {'proxy': '39.99.238.109:17897', 'active': True},
        {'proxy': '8.142.137.58:17897', 'active': True},
        {'proxy': '8.142.70.111:17897', 'active': True},
        {'proxy': '39.99.250.139:17897', 'active': True},
        {'proxy': '39.98.108.35:17897', 'active': True},
        {'proxy': '8.142.86.125:17897', 'active': True},
        {'proxy': '39.103.134.67:17897', 'active': True},
        {'proxy': '121.89.213.83:17897', 'active': True},
        {'proxy': '39.103.157.148:17897', 'active': True},
        {'proxy': '121.89.211.11:17897', 'active': True},
        {'proxy': '39.101.134.27:17897', 'active': True},
        {'proxy': '39.103.129.39:17897', 'active': True},
        {'proxy': '39.103.170.156:17897', 'active': True},
        {'proxy': '8.142.169.88:17897', 'active': True},
        {'proxy': '39.103.231.80:17897', 'active': True},
        {'proxy': '8.142.43.168:17897', 'active': True},
        {'proxy': '8.142.120.245:17897', 'active': True},
        {'proxy': '8.142.120.174:17897', 'active': True},
    ]
    APPLE_DEVELOPER_API_PROXY = {
        # 代理的作用，主要是为了加快苹果api的访问，在国内会出现卡死，访问超时等问题，怀疑是被苹果服务器拦截了
        # 'http': '47.243.172.202:17897',
        # 'https': '47.243.172.202:17897'
    }
    APPLE_DEVELOPER_API_TIMEOUT = 2 * 60  # 访问苹果api超时时间，默认3分钟
    MOBILE_CONFIG_SIGN_SSL = {
        # 描述文件是否签名，默认是关闭状态；如果开启，并且ssl_key_path 和 ssl_pem_path 正常，则使用填写的ssl进行签名,否则默认不签名
        'open': True,
        'ssl_key_path': f'/data/cert/{DOMAINCONF.API_DOMAIN.split("://")[1]}.key',
        'ssl_pem_path': f'/data/cert/{DOMAINCONF.API_DOMAIN.split("://")[1]}.pem'
    }
    DEFAULT_MOBILEPROVISION = {
        # 默认描述文件路径或者下载路径，用户企业签名或者超级签名 跳转 [设置 - 通用 - 描述文件|设备管理] 页面
        # 如果配置了path路径，则走路径，如果配置了url，则走URL，path 优先级大于url优先级
        'enterprise': {
            'url': '{{MOBILEPROVISION}}',
            # 'path': os.path.join(BASE_DIR,'files', 'embedded.mobileprovision'),
        },
        'supersign': {
            # 超级签名，如果self 为True，则默认用自己的描述文件，否则同企业配置顺序一致,自己的配置文件有时候有问题
            'self': False,
            'url': '{{MOBILEPROVISION}}',
            # 'path': os.path.join(BASE_DIR,'files', 'embedded.mobileprovision'),
        }
    }


class PAYCONF(object):
    PAY_SUCCESS_URL = '{{WEB_DOMAIN}}/user/orders'  # 前端页面，支付成功跳转页面
    APP_NOTIFY_URL = '{{API_DOMAIN}}/api/v1/fir/server/pay_success'  # 支付支付回调URL
    PAY_CONFIG_KEY_INFO = [
        {
            'NAME': 'alipay',
            'TYPE': 'ALI',
            'ENABLED': True,
            'AUTH': {
                'APP_ID': "2021002138691845",
                'APP_PRIVATE_KEY': '''-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAhqf2mwftoxZDNpl4eWsQ6mEfXgMlNPr6jv72ecA4hbKWqChXQmGS1T+0VsRTSoOXRDlu1MMqkTGISzHvmGb7Gmw+Myfs/ojoonD9r8fODvIo1MHolFBhr3GNQu7tqBlVJ76QgiYft+c4kkqCguuyCrd3Te6C5zCIuh6O98r4D3A3LFcm6OdScWGcfEbR+FUv+jSi2oezHeSpkhhpHGBLSsI0L9JOdHetdUE/TwN8V1HABdpnPXtp9SIu6ioIrrligX1ZRlwht2YUt0BPqPp/ApLdRIsqlhD4/ejmtMlaRqqiN6PulEThBew/qaLVSXIr2HCSXtwbki3pFMFOcsjF2wIDAQABAoIBADp4sQL83FnXDvSki8XdkgjUh7RhFUT+PtLdL9YKfADCXd1DNzDiAcqL0RlkQu62WXcMoW3OGavWoGJWmr3I6fy9R/0atzSH6syu19n+nyGqUcShNwdAKErwufB4o8Y8yddqToHVYCyRQOV1aVrEUhmJNUsn6LvPPW/kWRyMjE7XQDFHpL5/Ly7pXe+f9Btm37ZuePTPsm65P88C3GznjZxXhY1LBWFKLPG1470xdReduyeJFZS/TmK0nUxLwkACm9Gfvp7S2KJ3okUXohsGBAgJ68B9YeGiuIJiZhH2DZ1pm3/R9bSpOX3H+6vjaCsacXT5w7LZB+O0Vkthcm9vqeECgYEAvozFkIkFXXCEmCr3QVCJs4Fc6onbXEJU45xxubPhkA1wwwPrSqdubo4RHvNIus45Fn4mLzuQsaPRyJJZajvaKWC00GxhChMYj+nWgkAmABPKGwkMxzjC7wvEJkGyt87fHpK1XMFWQgfJ42VwUtmyemCMuh+A2SOekIJay93xTtkCgYEAtOhmQ4pu2cyqTzT+SD7p/VnS4sNqqM4I8NSvTuLkEo2IHnUj7YG6XoPZjn35dBvYUWWN2dwgfHXGEEzCOIwfy8GPA4eoKCDNEkMvoBVLdrEzMqg5QwG5GsIGvOuFnAzAw+D5YwEym/qmC2oBbat5jsAGT2rMmU5MnaS8a7lvcdMCgYEAiusQQb5TZfrZACMa3cg8i9y9A9R7UzicsM/mbW+B+8aAtfxOdr+4F+uE+d594IrmPcq8ReUUKR34nFRt0bBO7amuSOEqofCoEIt3MsBXs+i5iJpBcaClJSeb2hQ9mhm8uopUpInjPAJ3okva5twFbYikMDE1e5inSk1uqoBlI4kCgYB4rzDJjeg1U9upy2h3OcFPSkTtEgBtbEV6o+fvcF1GIzTTXMIDB7AUrVDNRizL0GeWpXDkDX1+ifL/nLVUk+YCP7XwXOdJHdiwfjGfUZVuMPg+qwrIMLYTq6xjC5uuZrOR+NtluL7SX3u10ZnyV5pYKLIM+OpUu29RGzy3gJVgEQKBgCC9vXS7P9RHTAxYEG4WOzv0tjFUtPOsaHenvNbc7nVe2Kkre0/TO+EtnuhINmJp2y5UEve6cLK2sPnbT8raarjPuomDfN0hwEx3jZd+rPdB/tdRH0LMLBu28TlzHllJYjbINn+NXc0adbqeuA4ziXTZow5yX5J+i9dy55A1bvie
-----END RSA PRIVATE KEY-----''',
                'ALI_PUBLIC_KEY': '''-----BEGIN CERTIFICATE-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAkru1ulQV1v4q+q38nyzgkdd3evf7C1/Ipu6K+ZFb5FiuxJ7mildkBSuKz/8+TRd+tjgk2lfc2ehK5pja3cxDO/nb25sBoWiU09rtxgXLehLsgRRhatbICrlOnYxg5aiB5odAp3NMRqore4lnVYwfIyL9M49I0G/NbQzYjUQvAQJsnHwc6a6Kuqi1CwR1WXI0sDF9w7KXC4vRFFIUTwI4bVq4HQWI7NhbgEajHM/j6D6Bh/OMcTYnJJzCja0WmZRe5flfCsELlPESOCWUMbYoaNfBzpNvvyOpmRgs9jgy2WY9SeaB9hxwkpr8tOd2Sc7j3221JKCyDaFAX+4zPy7/fQIDAQAB
-----END CERTIFICATE-----''',
                'APP_NOTIFY_URL': '{{APP_NOTIFY_URL}}',  # 支付支付回调URL
                'RETURN_URL': '{{PAY_SUCCESS_URL}}',  # 支付前端页面回调URL
                'SUBJECT': '向 FLY分发平台 充值',
            }
        },
        {
            'TYPE': 'WX',
            'NAME': 'wxpay',
            'ENABLED': True,
            'AUTH': {
                'APP_ID': "wx390e5985fd3699e6",
                'MCH_ID': "1608486112",
                'SERIAL_NO': "27DADA4D2921CDD66B8B20A68276F09B90754922",
                'APP_PRIVATE_KEY': '''-----BEGIN PRIVATE KEY-----
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
-----END PRIVATE KEY-----''',
                'API_V3_KEY': '60DbP621a9C3162dDd4AB9c2O15a005L',
                'APP_NOTIFY_URL': '{{APP_NOTIFY_URL}}',  # 支付支付回调URL
                'RETURN_URL': '{{PAY_SUCCESS_URL}}',  # 支付前端页面回调URL
                'SUBJECT': '向 FLY分发平台 充值',
            }
        }
    ]


class DOWNLOADTIMESCONF(object):
    SIGN_EXTRA_MULTIPLE = 2  # 超级签名消耗额外倍数，超级签名需要占用的服务大量资源

    # 具体计算方式查看该函数 get_app_d_count_by_app_id
    APP_USE_BASE_DOWNLOAD_TIMES = 100  # 单个应用下载消费点数
    APP_FILE_CALCULATION_UNIT = 1024 * 1024 * 100  # 应用计算次数，表示应用大小计算点数

    OSS_EXCHANGE_DOWNLOAD_TIMES = "{% widthratio 5 1 {{APP_USE_BASE_DOWNLOAD_TIMES}}  %}"  # 默认 1G 一个月 500下载点数

    PRIVATE_OSS_DOWNLOAD_TIMES = 4  # 私有存储单个应用下载消费点数

    USER_FREE_DOWNLOAD_TIMES = "{% widthratio 5 1 {{APP_USE_BASE_DOWNLOAD_TIMES}}  %}"  # 用户每日免费下载点数
    AUTH_USER_FREE_DOWNLOAD_TIMES = '{% widthratio 10 1 {{APP_USE_BASE_DOWNLOAD_TIMES}}  %}'  # 认证用户每日免费下载点数
    NEW_USER_GIVE_DOWNLOAD_TIMES = "{% widthratio 100 1 {{APP_USE_BASE_DOWNLOAD_TIMES}}  %}"  # 新用户注册赠送下载点数
    AUTH_USER_GIVE_DOWNLOAD_TIMES = "{% widthratio 200 1 {{APP_USE_BASE_DOWNLOAD_TIMES}}  %}"  # 用户认证成功赠送下载点数


class APPLEDEVELOPERCONF(object):
    # (-1, '疑似被封'), (0, '未激活'), (1, '已激活'), (2, '协议待同意'), (3, '维护中'), (4, '证书过期'), (5, '状态异常')
    # 开发者可用于签名的查询
    DEVELOPER_SIGN_STATUS = [AppleDeveloperStatus.ACTIVATED]

    # 开发者可用状态，详情查看 model.AppIOSDeveloperInfo
    DEVELOPER_USE_STATUS = [AppleDeveloperStatus.ACTIVATED, AppleDeveloperStatus.AGREEMENT_NOT_AGREED,
                            AppleDeveloperStatus.MAINTENANCE, AppleDeveloperStatus.CERTIFICATE_EXPIRED,
                            AppleDeveloperStatus.CERTIFICATE_MISSING, AppleDeveloperStatus.DEVICE_ABNORMAL,
                            AppleDeveloperStatus.ABNORMAL_STATUS]

    # 定时认证自动检测
    DEVELOPER_AUTO_CHECK_STATUS = [AppleDeveloperStatus.ACTIVATED, AppleDeveloperStatus.AGREEMENT_NOT_AGREED,
                                   AppleDeveloperStatus.CERTIFICATE_EXPIRED, AppleDeveloperStatus.CERTIFICATE_MISSING,
                                   AppleDeveloperStatus.DEVICE_ABNORMAL, AppleDeveloperStatus.ABNORMAL_STATUS]
    # 开发者api写操作查询[该状态用于苹果api接口]
    DEVELOPER_WRITE_STATUS = [AppleDeveloperStatus.ACTIVATED, AppleDeveloperStatus.MAINTENANCE,
                              AppleDeveloperStatus.CERTIFICATE_EXPIRED, AppleDeveloperStatus.DEVICE_ABNORMAL]

    # 开发者不可 修改为状态，用户前端控制
    DEVELOPER_DISABLED_STATUS = [AppleDeveloperStatus.AGREEMENT_NOT_AGREED, AppleDeveloperStatus.CERTIFICATE_EXPIRED,
                                 AppleDeveloperStatus.CERTIFICATE_MISSING, AppleDeveloperStatus.DEVICE_ABNORMAL]

    # 重签状态
    DEVELOPER_RESIGN_STATUS = [AppleDeveloperStatus.ACTIVATED, AppleDeveloperStatus.DEVICE_ABNORMAL,
                               AppleDeveloperStatus.MAINTENANCE]

    """
    DEVELOPER_WAIT_STATUS 开发者等待状态，详情查看 model.AppIOSDeveloperInfo 和 DEVELOPER_WAIT_ABNORMAL_STATE 状态有关
    
    DEVELOPER_WAIT_ABNORMAL_STATE 开发者异常状态是否等待,True 表示等待直到开发者状态恢复正常，并且设备注册成功 ，False 表示忽略，
                                    继续下一个新开发者账户
    """
    DEVELOPER_WAIT_STATUS = [AppleDeveloperStatus.MAINTENANCE, AppleDeveloperStatus.CERTIFICATE_EXPIRED,
                             AppleDeveloperStatus.CERTIFICATE_MISSING, AppleDeveloperStatus.ABNORMAL_STATUS]

    DEVELOPER_WAIT_ABNORMAL_STATE = True

    # 开发者共享给其他第三方用户， 中间必须包含 : 前端需要根据 : 进行分割
    DEVELOPER_UID_KEY = "T:"

    """
    DEVELOPER_WAIT_ABNORMAL_DEVICE  异常设备注册是否等待,True 表示等待直到注册成功，False 表示忽略，继续下一个新开发者账户
    DEVELOPER_ABNORMAL_DEVICE_WRITE 受DEVELOPER_WAIT_ABNORMAL_DEVICE影响，当DEVELOPER_WAIT_ABNORMAL_DEVICE 为True 才生效
                                    异常设备注册等待中是否还继续注册新设备, True 表示设备异常下继续注册新设备
    """
    DEVELOPER_WAIT_ABNORMAL_DEVICE = True
    DEVELOPER_ABNORMAL_DEVICE_WRITE = False


class CONFIGDESCRIPTION(object):
    DEVELOPER_WAIT_ABNORMAL_DEVICE_DES = '【异常设备注册等待】：开启 表示等待直到注册成功，关闭 表示忽略。' \
                                         'ps：异常设备指 设备注册到开发者，但是设备状态为 “不合格”，“处理中” 时，既设备不可用，' \
                                         '开启等待，则等待设备状态恢复正常，最大避免设备数重复消耗'
    DEVELOPER_ABNORMAL_DEVICE_WRITE_DES = '【异常设备注册等待中继续注册新设备】：开启 表示新设备还可以注册该 设备异常 开发者中，关闭 表示忽略。 ' \
                                          'ps：该配置仅当开启【异常设备注册等待】时生效'
    DEVELOPER_WAIT_ABNORMAL_STATE_DES = '【开发者异常状态是否等待】：开启 表示等待直到开发者状态恢复正常，并且设备注册成功，关闭 表示忽略。 ps：当开发者状态为 ' \
                                        '“维护”，“证书丢失”，“证书过期”，“异常状态时”，开启等待，可以最大的避免设备数重复消耗 '


class USERPERSONALCONFIGKEY(object):
    DEVELOPER_STATUS_CONFIG = ['DEVELOPER_WAIT_ABNORMAL_STATE', 'DEVELOPER_WAIT_ABNORMAL_DEVICE',
                               'DEVELOPER_ABNORMAL_DEVICE_WRITE']
    PREVIEW_ROUTE_HASH = False  # 预览路由模式是否是hash,  如果使用hash模式，url中就会存在“#“符号，这个符号后面的是路径。


class OSSSTORAGECONF(object):
    STORAGE_FREE_CAPACITY = 2048 * 1024 * 1024  # 单位byte 2G
    STORAGE_OSS_CAPACITY = 1024 * 1024 * 1024 * 1024  # 单位byte 1T
    STORAGE_ALLOW_ENDPOINT = [
        'oss-cn-beijing-internal.aliyuncs.com',
        'oss-cn-zhangjiakou-internal.aliyuncs.com'
    ]

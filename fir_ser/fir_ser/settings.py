"""
Django settings for fir_ser project.

Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

from celery.schedules import crontab

from config import *

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = BASECONF.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = BASECONF.DEBUG

ALLOWED_HOSTS = BASECONF.ALLOWED_HOSTS

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api.apps.ApiConfig',
    'rest_framework',
    'captcha',
    'django_celery_beat',
    'django_celery_results',
    'corsheaders',
    'django_filters',
    'xsign.apps.ApiConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'fir_ser.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), os.path.join(BASE_DIR, 'common/libs/sendmsg/templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'fir_ser.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    # },
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': DBCONF.name,
        'USER': DBCONF.user,
        'PASSWORD': DBCONF.password,
        'HOST': DBCONF.host,
        'PORT': DBCONF.port,
        'CONN_MAX_AGE': 600,
        # 设置MySQL的驱动
        # 'OPTIONS': {'init_command': 'SET storage_engine=INNODB'},
        'OPTIONS': {'init_command': 'SET sql_mode="STRICT_TRANS_TABLES"', 'charset': 'utf8mb4'}
    },
    # 'slave': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'NAME': DBCONF.name,
    #     'USER': DBCONF.user,
    #     'PASSWORD': DBCONF.password,
    #     'HOST': DBCONF.host,
    #     'PORT': DBCONF.port,
    #     'CONN_MAX_AGE': 600,
    #     # 设置MySQL的驱动
    #     # 'OPTIONS': {'init_command': 'SET storage_engine=INNODB'},
    #     'OPTIONS': {'init_command': 'SET sql_mode="STRICT_TRANS_TABLES"', 'charset': 'utf8mb4'}
    # }
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'NAME': DBCONF.name,
    #     'USER': DBCONF.user,
    #     'PASSWORD': DBCONF.password,
    #     'HOST': DBCONF.host,
    #     'PORT': DBCONF.port,
    #     'CONN_MAX_AGE': 3600,
    #     'OPTIONS': {
    #         'client_encoding': 'UTF8',
    #         # 'default_transaction_isolation': 'read committed'
    #
    #     },
    # }
    # https://www.postgresql.org/download/linux/redhat/
    # psql -U postgres
    # CREATE USER flyuser WITH PASSWORD 'KGzKjZpWBp4R4RSa';
    # create database flyapp with owner=flyuser;

}

# 读写分离 可能会出现 the current database router prevents this relation.
# 1.项目设置了router读写分离，且在ORM create()方法中，使用了前边filter()方法得到的数据，
# 2.由于django是惰性查询，前边的filter()并没有立即查询，而是在create()中引用了filter()的数据时，执行了filter()，
# 3.此时写操作的db指针指向write_db，filter()的db指针指向read_db，两者发生冲突，导致服务禁止了此次与mysql的交互
# 解决办法：
# 在前边filter()方法中，使用using()方法，使filter()方法立即与数据库交互，查出数据。

# DATABASE_ROUTERS = ['common.core.dbrouter.DBRouter']

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        # 'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_THROTTLE_CLASSES': [
        'common.core.throttle.LoginUserThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': BASECONF.DEFAULT_THROTTLE_RATES,
    'EXCEPTION_HANDLER': 'common.core.exception.common_exception_handler',

}
# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/statics/'

# python manage.py collectstatic 收集到的静态文件
STATIC_ROOT = os.path.join(BASE_DIR, "api-static")

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "statics")
]

# Media配置
MEDIA_URL = "files/"
MEDIA_ROOT = os.path.join(BASE_DIR, "files")
# supersign配置
SUPER_SIGN_ROOT = os.path.join(BASE_DIR, "supersign")

AUTH_USER_MODEL = "api.UserInfo"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://%s:%s/1" % (CACHECONF.host, CACHECONF.port),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {"max_connections": 100},
            "PASSWORD": CACHECONF.password,
            "DECODE_RESPONSES": True
        },
        "TIMEOUT": 60 * 15
    },
}

# DRF扩展缓存时间
REST_FRAMEWORK_EXTENSIONS = {
    # 缓存时间
    'DEFAULT_CACHE_RESPONSE_TIMEOUT': 3600,
    # 缓存存储
    'DEFAULT_USE_CACHE': 'default',
}
# 取消自动加斜杠
APPEND_SLASH = False

# https://pypi.org/project/django-cors-headers/

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'POST',
    'PUT',
)

CORS_ALLOW_HEADERS = (
    'XMLHttpRequest',
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "x-token"
)

CACHE_KEY_TEMPLATE = {
    'config_key': 'config',
    'task_state_key': 'task_state',
    'pending_state_key': 'pending_state',
    'wx_login_bind_key': 'wx_login_bind',
    'notify_loop_msg_key': 'notify_loop_msg',
    'user_can_download_key': 'user_can_download',
    'download_times_key': 'app_download_times',
    'make_token_key': 'make_token',
    'ad_pic_show_key': 'ad_pic_show',
    'download_short_key': 'download_short',
    'download_short_show_key': 'download_short_show',
    'app_instance_key': 'app_instance',
    'download_url_key': 'download_url',
    'user_storage_key': 'storage_auth',
    'user_auth_token_key': 'user_auth_token',
    'download_today_times_key': 'download_today_times',
    'developer_auth_code_key': 'developer_auth_code',
    'upload_file_tmp_name_key': 'upload_file_tmp_name',
    'login_failed_try_times_key': 'login_failed_try_times',
    'user_free_download_times_key': 'user_free_download_times',
    'super_sign_failed_send_msg_times_key': 'super_sign_failed_send_msg_times',
    'wx_access_token_key': 'wx_basic_access_token',
    'wx_ticket_info_key': 'wx_ticket_info',
    'ipa_sign_udid_queue_key': 'ipa_sign_udid_queue',
    'ip_proxy_store_list_key': 'ip_proxy_store_list',
    'ip_proxy_store_active_key': 'ip_proxy_store_active',
}

DATA_DOWNLOAD_KEY = "d_token"
FILE_UPLOAD_TMP_KEY = ".tmp"

SYNC_CACHE_TO_DATABASE = {
    'download_times': 10,  # 下载次数同步时间
    'best_proxy_ips_times': 6 * 60 * 60,  # 代理ip 自动获取时间
    'wx_get_access_token_times': 60 * 10,  # 微信access_token 自动获取时间
    'try_login_times': (10, 12 * 60 * 60),  # 当天登录失败次数，超过该失败次数，锁定24小时
    'auto_clean_tmp_file_times': 60 * 30,  # 定时清理上传失误生成的临时文件
    'auto_clean_captcha_store_times': 60 * 60,  # 定时清理临时验证码数据
    'auto_clean_local_tmp_file_times': 60 * 30,  # 定时清理临时文件,现在包含超级签名描述临时文件
    'try_send_msg_over_limit_times': (3, 60 * 60),  # 每小时用户发送信息次数
    'clean_local_tmp_file_from_mtime': 60 * 60,  # 清理最后一次修改时间超过限制时间的临时文件,单位秒
    'auto_check_ios_developer_active_times': 60 * 60 * 12,  # ios开发者证书检测时间
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

CAPTCHA_TIMEOUT = 5  # Minutes
CAPTCHA_LENGTH = 6  # Chars

BASE_LOG_DIR = os.path.join(BASE_DIR, "logs", "api")
if not os.path.isdir(BASE_LOG_DIR):
    os.makedirs(BASE_LOG_DIR)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s][%(threadName)s:%(thread)d][task_id:%(name)s][%(filename)s:%(lineno)d]'
                      '[%(levelname)s][%(message)s]'
        },
        'simple': {
            'format': '[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d]%(message)s'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],  # 只有在Django debug为True时才在屏幕打印日志
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'TF': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件，根据时间自动切
            'filename': os.path.join(BASE_LOG_DIR, "flyapp_info.log"),  # 日志文件
            'maxBytes': 1024 * 1024 * 50,  # 日志大小 50M
            'backupCount': 10,  # 备份数为3  xx.log --> xx.log.2018-08-23_00-00-00 --> xx.log.2018-08-24_00-00-00 --> ...
            # 'when': 'W6',  # 每天一切， 可选值有S/秒 M/分 H/小时 D/天 W0-W6/周(0=周一) midnight/如果没指定时间就默认在午夜
            'formatter': 'standard',
            'encoding': 'utf-8',
        },
        'error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件，自动切
            'filename': os.path.join(BASE_LOG_DIR, "flyapp_err.log"),  # 日志文件
            'maxBytes': 1024 * 1024 * 50,  # 日志大小 50M
            'backupCount': 10,
            'formatter': 'standard',
            'encoding': 'utf-8',
        },
        'warning': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件，自动切
            'filename': os.path.join(BASE_LOG_DIR, "flyapp_warning.log"),  # 日志文件
            'maxBytes': 1024 * 1024 * 50,  # 日志大小 50M
            'backupCount': 10,
            'formatter': 'standard',
            'encoding': 'utf-8',
        },
        'pay': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件，自动切
            'filename': os.path.join(BASE_LOG_DIR, "flyapp_pay.log"),  # 日志文件
            'maxBytes': 1024 * 1024 * 50,  # 日志大小 50M
            'backupCount': 10,
            'formatter': 'standard',
            'encoding': 'utf-8',
        },
        'sql': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件，自动切
            'filename': os.path.join(BASE_LOG_DIR, "flyapp_sql.log"),  # 日志文件
            'maxBytes': 1024 * 1024 * 50,  # 日志大小 50M
            'backupCount': 10,
            'formatter': 'standard',
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        '': {  # 默认的logger应用如下配置
            'handlers': ['TF', 'console', 'error', 'warning'],  # 上线之后可以把'console'移除
            'level': 'DEBUG',
            'propagate': True,
        },
        'pay': {  # 默认的logger应用如下配置
            'handlers': ['pay'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['console', 'sql'],
            'propagate': True,
            'level': 'INFO',
        },
    },
}

# 结果存放到Django|redis
# CELERY_RESULT_BACKEND = 'django-db'
# CELERY_RESULT_BACKEND = 'django-cache'
# result_backend = 'redis://username:password@host:port/db'
# result_backend = 'redis://:password@host:port/db'
CELERY_RESULT_BACKEND = 'django-db'
# CELERY_RESULT_BACKEND = 'db+sqlite:///results.sqlite'


# broker redis|mq
DJANGO_DEFAULT_CACHES = CACHES['default']
CELERY_BROKER_URL = 'redis://:%s@%s/2' % (
    DJANGO_DEFAULT_CACHES["OPTIONS"]["PASSWORD"], DJANGO_DEFAULT_CACHES["LOCATION"].split("/")[2])
# CELERY_BROKER_URL = 'amqp://guest@localhost//'
#: Only add pickle to this list if your broker is secured


CELERY_WORKER_CONCURRENCY = 30  # worker并发数
CELERYD_FORCE_EXECV = True  # 非常重要,有些情况下可以防止死
CELERY_RESULT_EXPIRES = 3600  # 任务结果过期时间

CELERY_WORKER_DISABLE_RATE_LIMITS = True  # 任务发出后，经过一段时间还未收到acknowledge , 就将任务重新交给其他worker执行
CELERY_WORKER_PREFETCH_MULTIPLIER = 60  # celery worker 每次去redis取任务的数量

CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000  # 每个worker执行了多少任务就会死掉，我建议数量可以大一些，比如200

CELERY_ENABLE_UTC = False
DJANGO_CELERY_BEAT_TZ_AWARE = False
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

CELERY_BEAT_SCHEDULE = {
    'sync_download_times_job': {
        'task': 'api.tasks.sync_download_times_job',
        'schedule': SYNC_CACHE_TO_DATABASE.get("download_times"),
        'args': ()
    },
    'check_bypass_status_job': {
        'task': 'api.tasks.check_bypass_status_job',
        'schedule': BASECONF.GEETEST_CYCLE_TIME,
        'args': ()
    },
    'auto_clean_upload_tmp_file_job': {
        'task': 'api.tasks.auto_clean_upload_tmp_file_job',
        'schedule': SYNC_CACHE_TO_DATABASE.get("auto_clean_tmp_file_times"),
        'args': ()
    },
    'auto_delete_tmp_file_job': {
        'task': 'api.tasks.auto_delete_tmp_file_job',
        'schedule': SYNC_CACHE_TO_DATABASE.get("auto_clean_local_tmp_file_times"),
        'args': ()
    },
    'auto_clean_captcha_store_job': {
        'task': 'api.tasks.auto_clean_captcha_store_job',
        'schedule': SYNC_CACHE_TO_DATABASE.get("auto_clean_captcha_store_times"),
        'args': ()
    },
    'auto_clean_remote_client_job': {
        'task': 'api.tasks.auto_clean_remote_client_job',
        # 'schedule': SYNC_CACHE_TO_DATABASE.get("auto_check_ios_developer_active_times"),
        'schedule': crontab(hour=1, minute=1),
        'args': ()
    },
    'download_times_notify_check_job': {
        'task': 'api.tasks.download_times_notify_check_job',
        # 'schedule': SYNC_CACHE_TO_DATABASE.get("auto_check_ios_developer_active_times"),
        'schedule': crontab(hour='6,12,18', minute=10),
        'args': ()
    },
    'apple_developer_devices_check_job': {
        'task': 'api.tasks.apple_developer_devices_check_job',
        # 'schedule': SYNC_CACHE_TO_DATABASE.get("auto_check_ios_developer_active_times"),
        'schedule': crontab(hour='6,12,18', minute=20),
        'args': ()
    },
    'apple_developer_cert_notify_check_job': {
        'task': 'api.tasks.apple_developer_cert_notify_check_job',
        # 'schedule': SYNC_CACHE_TO_DATABASE.get("auto_check_ios_developer_active_times"),
        'schedule': crontab(hour=2, minute=1),
        'args': ()
    },
    'sync_wx_access_token_job': {
        'task': 'api.tasks.sync_wx_access_token_job',
        'schedule': SYNC_CACHE_TO_DATABASE.get("wx_get_access_token_times"),
        'args': (),
    },
    # 'get_best_proxy_ips_job': {
    #     'task': 'xsign.tasks.get_best_proxy_ips_job',
    #     'schedule': SYNC_CACHE_TO_DATABASE.get("best_proxy_ips_times"),
    #     'args': (),
    # },
    'auto_check_ios_developer_active_job': {
        'task': 'xsign.tasks.auto_check_ios_developer_active_job',
        # 'schedule': SYNC_CACHE_TO_DATABASE.get("auto_check_ios_developer_active_times"),
        'schedule': crontab(hour=1, minute=1),
        'args': ()
    },
    'auto_clean_sign_log_job': {
        'task': 'xsign.tasks.auto_clean_sign_log_job',
        'schedule': crontab(hour=2, minute=2),
        'args': ()
    },
}

# listen port

SERVER_BIND_HOST = BASECONF.SERVER_BIND_HOST
SERVER_LISTEN_PORT = BASECONF.SERVER_LISTEN_PORT
CELERY_FLOWER_PORT = BASECONF.CELERY_FLOWER_PORT
CELERY_FLOWER_HOST = BASECONF.CELERY_FLOWER_HOST

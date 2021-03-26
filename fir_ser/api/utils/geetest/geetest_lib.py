import random
import json
import requests
import hmac
import hashlib

from .geetest_lib_result import GeetestLibResult


# sdk lib包，核心逻辑。
class GeetestLib:
    IS_DEBUG = False  # 调试开关，是否输出调试日志
    API_URL = "http://api.geetest.com"
    REGISTER_URL = "/register.php"
    VALIDATE_URL = "/validate.php"
    JSON_FORMAT = "1"
    NEW_CAPTCHA = True
    HTTP_TIMEOUT_DEFAULT = 5  # 单位：秒
    VERSION = "python-flask:3.1.1"
    GEETEST_CHALLENGE = "geetest_challenge"  # 极验二次验证表单传参字段 chllenge
    GEETEST_VALIDATE = "geetest_validate"  # 极验二次验证表单传参字段 validate
    GEETEST_SECCODE = "geetest_seccode"  # 极验二次验证表单传参字段 seccode

    def __init__(self, geetest_id, geetest_key):
        self.geetest_id = geetest_id
        self.geetest_key = geetest_key
        self.libResult = GeetestLibResult()

    def gtlog(self, message):
        if self.IS_DEBUG:
            print("gtlog: " + message)

    # 验证初始化
    def register(self, digestmod, param_dict):
        self.gtlog("register(): 开始验证初始化, digestmod={0}.".format(digestmod))
        origin_challenge = self.request_register(param_dict)
        self.build_register_result(origin_challenge, digestmod)
        self.gtlog("register(): 验证初始化, lib包返回信息={0}.".format(self.libResult))
        return self.libResult

    def request_register(self, param_dict):
        param_dict.update({"gt": self.geetest_id, "sdk": self.VERSION, "json_format": self.JSON_FORMAT})
        register_url = self.API_URL + self.REGISTER_URL
        self.gtlog("requestRegister(): 验证初始化, 向极验发送请求, url={0}, params={1}.".format(register_url, param_dict))
        try:
            res = requests.get(register_url, params=param_dict, timeout=self.HTTP_TIMEOUT_DEFAULT)
            res_body = res.text if res.status_code == requests.codes.ok else ""
            self.gtlog("requestRegister(): 验证初始化, 与极验网络交互正常, 返回码={0}, 返回body={1}.".format(res.status_code, res_body))
            res_dict = json.loads(res_body)
            origin_challenge = res_dict["challenge"]
        except Exception as e:
            self.gtlog("requestRegister(): 验证初始化, 请求异常，后续流程走宕机模式, " + repr(e))
            origin_challenge = ""
        return origin_challenge

    def local_init(self):
        self.build_register_result("", "")
        self.gtlog("local_init(): bypass当前状态为fail，后续流程将进入宕机模式, " + self.libResult.data)
        return self.libResult

    # 构建验证初始化返回数据
    def build_register_result(self, origin_challenge, digestmod):
        # origin_challenge为空或者值为0代表失败
        if not origin_challenge or origin_challenge == "0":
            # 本地随机生成32位字符串
            challenge = "".join(random.sample('abcdefghijklmnopqrstuvwxyz0123456789', 32))
            data = json.dumps(
                {"success": 0, "gt": self.geetest_id, "challenge": challenge, "new_captcha": self.NEW_CAPTCHA})
            self.libResult.set_all(0, data, "bypass当前状态为fail，后续流程走宕机模式")
        else:
            if digestmod == "md5":
                challenge = self.md5_encode(origin_challenge + self.geetest_key)
            elif digestmod == "sha256":
                challenge = self.sha256_endode(origin_challenge + self.geetest_key)
            elif digestmod == "hmac-sha256":
                challenge = self.hmac_sha256_endode(origin_challenge, self.geetest_key)
            else:
                challenge = self.md5_encode(origin_challenge + self.geetest_key)
            data = json.dumps(
                {"success": 1, "gt": self.geetest_id, "challenge": challenge, "new_captcha": self.NEW_CAPTCHA})
            self.libResult.set_all(1, data, "")

    # 正常流程下（即验证初始化成功），二次验证
    def successValidate(self, challenge, validate, seccode, param_dict={}):
        self.gtlog(
            "successValidate(): 开始二次验证 正常模式, challenge={0}, validate={1}, seccode={2}.".format(challenge, validate,
                                                                                               seccode))
        if not self.check_param(challenge, validate, seccode):
            self.libResult.set_all(0, "", "正常模式，本地校验，参数challenge、validate、seccode不可为空")
        else:
            response_seccode = self.requestValidate(challenge, validate, seccode, param_dict)
            if not response_seccode:
                self.libResult.set_all(0, "", "请求极验validate接口失败")
            elif response_seccode == "false":
                self.libResult.set_all(0, "", "极验二次验证不通过")
            else:
                self.libResult.set_all(1, "", "")
        self.gtlog("successValidate(): 二次验证 正常模式, lib包返回信息={0}.".format(self.libResult))
        return self.libResult

    # 异常流程下（即验证初始化失败，宕机模式），二次验证
    # 注意：由于是宕机模式，初衷是保证验证业务不会中断正常业务，所以此处只作简单的参数校验，可自行设计逻辑。
    def failValidate(self, challenge, validate, seccode):
        self.gtlog(
            "failValidate(): 开始二次验证 宕机模式, challenge={0}, validate={1}, seccode={2}.".format(challenge, validate,
                                                                                            seccode))
        if not self.check_param(challenge, validate, seccode):
            self.libResult.set_all(0, "", "宕机模式，本地校验，参数challenge、validate、seccode不可为空.")
        else:
            self.libResult.set_all(1, "", "")
        self.gtlog("failValidate(): 二次验证 宕机模式, lib包返回信息={0}.".format(self.libResult))
        return self.libResult

    # 向极验发送二次验证的请求，POST方式
    def requestValidate(self, challenge, validate, seccode, param_dict):
        param_dict.update(
            {"seccode": seccode, "json_format": self.JSON_FORMAT, "challenge": challenge, "sdk": self.VERSION,
             "captchaid": self.geetest_id})
        validate_url = self.API_URL + self.VALIDATE_URL
        self.gtlog("requestValidate(): 二次验证 正常模式, 向极验发送请求, url={0}, params={1}.".format(validate_url, param_dict))
        try:
            res = requests.post(validate_url, data=param_dict, timeout=self.HTTP_TIMEOUT_DEFAULT)
            res_body = res.text if res.status_code == requests.codes.ok else ""
            self.gtlog(
                "requestValidate(): 二次验证 正常模式, 与极验网络交互正常, 返回码={0}, 返回body={1}.".format(res.status_code, res_body))
            res_dict = json.loads(res_body)
            seccode = res_dict["seccode"]
        except Exception as e:
            self.gtlog("requestValidate(): 二次验证 正常模式, 请求异常, " + repr(e))
            seccode = ""
        return seccode

    # 校验二次验证的三个参数，校验通过返回true，校验失败返回false
    def check_param(self, challenge, validate, seccode):
        return not (
                challenge is None or challenge.isspace() or validate is None or validate.isspace() or seccode is None or seccode.isspace())

    def md5_encode(self, value):
        md5 = hashlib.md5()
        md5.update(value.encode("utf-8"))
        return md5.hexdigest()

    def sha256_endode(self, value):
        sha256 = hashlib.sha256()
        sha256.update(value.encode("utf-8"))
        return sha256.hexdigest()

    def hmac_sha256_endode(self, value, key):
        return hmac.new(key.encode("utf-8"), value.encode("utf-8"), digestmod=hashlib.sha256).hexdigest()

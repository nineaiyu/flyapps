from django.conf import settings
from api.utils.geetest import GeeTestLib
def verify(verify_data, uid=None, extend_params=None):
    """第三方滑动验证码校验.

    选用第三方的验证组件, 根据参数进行校验
    根据布尔值辨别是否校验通过

    Parameters
    ----------

    verify_data : dict
        请求数据

    uid: string, default: None
        用户UID, 如果存在就免受滑动验证码的限制

    extend_params : dict
        预留的扩展参数

    Returns
    -------
    True OR False
    """
    captcha_config = settings.GEE_TEST
    if captcha_config.get("verify_status"):

        status = True

        if uid in captcha_config.get("not_verify"):
            return True

        gt = GeeTestLib(captcha_config["gee_test_access_id"], captcha_config["gee_test_access_key"])
        challenge = verify_data.get(gt.FN_CHALLENGE, '')
        validate = verify_data.get(gt.FN_VALIDATE, '')
        seccode = verify_data.get(gt.FN_SECCODE, '')
        # status = request.session.get(gt.GT_STATUS_SESSION_KEY, 1)
        # user_id = request.session.get("user_id")

        if status:
            result = gt.success_validate(challenge, validate, seccode, None)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        return True if result else False
    else:
        return True


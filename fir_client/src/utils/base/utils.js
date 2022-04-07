export function GetRandomNum(Min, Max) {
    const Range = Max - Min;
    const Rand = Math.random();
    return (Min + Math.round(Rand * Range));
}

export function getRandomStr(str_length = 32) {
    const SIGNING_v1 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'//36
    // const SIGNING_v2 ='ABCDEFGHJKMNPQRSTUVWXYZ23456789'//31
    // const SIGNING_v3 ='1234567890'//10
    // const SIGNING_v4 ='ABCDEFGHIJKLMNOPQRSTUVWXYZ'//26
    const SIGNING_v5 = 'abcdefghigklmnopqrstuvwxyz'//26
    let random_str = SIGNING_v1 + SIGNING_v5
    let random_code = ''
    str_length -= 1
    for (let i = 0; i < str_length; i++) {
        random_code = random_code + random_str[GetRandomNum(0, str_length)]
    }
    return random_code
}


export function checkEmail(email) {
    let re = /^(\w-*\.*)+@(\w-?)+(\.\w{2,})+$/;
    return re.test(email);
}

export function checkphone(email) {
    let re = /^1\d{10}$/;
    return re.test(email);
}


export function geetestbase(func, self, uid, params, callback, errback, readyback) {
    func(res => {
        if (res.code === 1000) {
            let data = res.data;
            // eslint-disable-next-line no-undef
            initGeetest({
                gt: data.gt,
                challenge: data.challenge,
                new_captcha: data.new_captcha, // 用于宕机时表示是新验证码的宕机
                offline: !data.success, // 表示用户后台检测极验服务器是否宕机，一般不需要关注
                product: "float", // 产品形式，包括：float，popup
                width: "100%"
            }, (captchaObj) => {
                self.$refs.captcha.innerHTML = '';
                captchaObj.appendTo("#captcha");
                captchaObj.onReady(() => {
                    readyback()
                }).onSuccess(() => {
                    params.geetest = captchaObj.getValidate();
                    callback(params);
                }).onError(() => {
                    captchaObj.destroy();
                });
            });
        } else {
            errback(res)
        }
    }, {
        "methods": "PUT",
        "data": {user_id: uid}
    });
}

export function format_time(stime) {
    if (stime) {
        stime = stime.split(".")[0].split("T");
        return stime[0] + " " + stime[1]
    } else
        return '';
}
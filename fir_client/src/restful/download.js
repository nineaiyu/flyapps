import Axios from 'axios'

Axios.defaults.withCredentials = true;

const DOMAIN = process.env.base_env.baseShortUrl;
const APIPATH = '/api/v1/fir/server';
let USERSEVER = DOMAIN + APIPATH;

function ErrorMsg(error) {
    if (error && error.response) {
        switch (error.response.status) {
            case 400:
                error.message = '请求错误(400)';
                break;
            case 403:
                error.message = '拒绝访问(403)';
                break;
            case 404:
                error.message = '请求出错(404)';
                break;
            case 429:
                error.message = '您的 IP 访问频繁，请稍后再次尝试';
                break;
            default:
                error.message = `连接出错(${error.response.status})!`;
        }
    } else {
        error.message = '连接服务器失败!';
    }
    if (error.message === 'Network Error') {
        alert('网络连接失败')
    }
}

function getData(methods = 'GET', url, params = {}, callBack) {


    var uri = '';
    var keys = Object.keys(params);
    var values = Object.values(params);
    for (var i = 0; i < keys.length; i++) {
        var key = keys[i];
        var value = values[i];
        uri = uri + key + "=" + value;
        if (i < keys.length - 1) {
            uri = uri + "&"
        }
    }
    if (uri !== "") {
        uri = "?" + uri
    }
    url = url + uri;

    if (methods === "PUT") {
        Axios
            .put(url, params)
            .then(function (response) {
                callBack(response.data);
            })
            .catch(function (error) {
                ErrorMsg(error);
                callBack({"code": -1});
            });
    } else if (methods === 'POST') {
        Axios
            .post(url, params)
            .then(function (response) {
                callBack(response.data);
            })
            .catch(function (error) {
                ErrorMsg(error);
                callBack({"code": -1});
            });
    } else
        Axios
            .get(url, params)
            .then(function (response) {
                callBack(response.data);
                let x = '';
                if (x !== '') {
                    alert(x)
                }
            })
            .catch(function (error) {
                ErrorMsg(error);
                callBack({"code": -1});
            });
}


/**根据短链接获取应用信息 */
export function getShortAppinfo(callBack, params) {
    getData(
        'GET',
        USERSEVER + '/short/' + params.short,
        params,
        data => {
            callBack(data);
        },
    );
}


/**获取下载的url */
export function getdownloadurl(callBack, params) {
    getData(
        'GET',
        USERSEVER + '/install/' + params.app_id,
        params.data,
        data => {
            callBack(data);
        },
    );
}


/**应用举报 */
export function appReport(callBack, params) {
    getData(
        params.methods,
        USERSEVER + '/report',
        params.data,
        data => {
            callBack(data);
        },
    );
}

/**token */
export function loginFun(callBack, params) {
    getData(
        params.methods,
        USERSEVER + '/login',
        params.data,
        data => {
            callBack(data);
        },
    );
}

/**获取验证token */
export function getAuthTokenFun(callBack, params) {
    getData(
        params.methods,
        USERSEVER + '/auth',
        params.data,
        data => {
            callBack(data);
        },
    );
}

export function checkEmail(email) {
    let re = /^(\w-*\.*)+@(\w-?)+(\.\w{2,})+$/;
    return re.test(email);
}

export function checkphone(email) {
    let re = /^1\d{10}$/;
    return re.test(email);
}

export function geetest(self, uid, params, callback) {
    loginFun(res => {
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
                }).onSuccess(() => {
                    params.geetest = captchaObj.getValidate();
                    callback(params);
                }).onError(() => {
                    captchaObj.destroy();
                });
            });
        } else {
            alert(res.msg);
        }
    }, {
        "methods": "PUT",
        "data": {user_id: uid}
    });
}

/** 超级签名************************************************相关api */

/**获取签名任务状态 */
let SIGNSEVER = DOMAIN + '/api/v1/fir/xsign';

export function gettask(callBack, params) {
    getData(
        'GET',
        SIGNSEVER + '/task/' + params.short,
        params.data,
        data => {
            callBack(data);
        },
    );
}
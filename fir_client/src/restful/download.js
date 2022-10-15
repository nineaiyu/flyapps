import Axios from 'axios'
import {geetestbase} from "@/utils/base/utils";

const DOMAIN = process.env.base_env.baseShortUrl;

const USERSEVER = 'api/v1/fir/server';
// eslint-disable-next-line no-console
console.log("js build version:" + process.env.base_env.version);
// create an axios instance
const service = Axios.create({
    baseURL: DOMAIN, // url = base url + request url
    withCredentials: true, // send cookies when cross-domain requests
    timeout: 120000 // request timeout
})


function ErrorMsg(error, callBack) {
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
    callBack({code: -1, msg: error.message})
}

function responseMiddleware(data, callBack) {
    if (data.code === 999) {
        window.alert(data.detail)
    } else {
        callBack(data);
    }
}

function getData(methods = 'GET', url, params = {}, callBack) {

    if (methods === "PUT") {
        service
            .put(url, params)
            .then(function (response) {
                responseMiddleware(response.data, callBack);
            })
            .catch(function (error) {
                ErrorMsg(error, callBack);
            });
    } else if (methods === 'POST') {
        service
            .post(url, params)
            .then(function (response) {
                responseMiddleware(response.data, callBack);
            })
            .catch(function (error) {
                ErrorMsg(error, callBack);
            });
    } else
        service
            .get(url, {params: params})
            .then(function (response) {
                responseMiddleware(response.data, callBack);
            })
            .catch(function (error) {
                ErrorMsg(error, callBack);
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


export function geetest(self, uid, params, callback) {
    return geetestbase(loginFun, self, uid, params, callback, res => {
        window.alert(res.msg);
    })
}

/** 超级签名************************************************相关api */

/**获取签名任务状态 */
let SIGNSEVER = DOMAIN + '/api/v1/fir/xsign';

export function gettask(callBack, params) {
    getData(
        params.methods,
        SIGNSEVER + '/task/' + params.short,
        params.data,
        data => {
            callBack(data);
        },
    );
}

import Axios from 'axios'
import VueCookies from 'vue-cookies'
import router from "@/router";

const Base64 = require('js-base64').Base64;
Axios.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded';
Axios.defaults.withCredentials = true;
// Axios.defaults.httpsAgent = new https.Agent({
//     keepAlive: true
// });
const controller = new AbortController();

export function requestAbort() {
    controller.abort();
}

// eslint-disable-next-line no-console
console.log("flyapps js version:" + process.env.base_env.version);

const DOMAIN = process.env.base_env.baseUrl;
const APIPATH = '/api/v1/fir/server';
let USERSEVER = DOMAIN + APIPATH;

export function convertRes2Blob(response) {
    // 提取文件名
    const fileName = response.headers['content-disposition'].match(
        /filename=(.*)/
    )[1];
    // 将二进制流转为blob
    const blob = new Blob([response.data], {type: 'application/octet-stream'});
    if (typeof window.navigator.msSaveBlob !== 'undefined') {
        // 兼容IE，window.navigator.msSaveBlob：以本地方式保存文件
        window.navigator.msSaveBlob(blob, decodeURI(fileName))
    } else {
        // 创建新的URL并指向File对象或者Blob对象的地址
        const blobURL = window.URL.createObjectURL(blob);
        // 创建a标签，用于跳转至下载链接
        const tempLink = document.createElement('a');
        tempLink.style.display = 'none';
        tempLink.href = blobURL;
        tempLink.setAttribute('download', decodeURI(fileName));
        // 兼容：某些浏览器不支持HTML5的download属性
        if (typeof tempLink.download === 'undefined') {
            tempLink.setAttribute('target', '_blank')
        }
        // 挂载a标签
        document.body.appendChild(tempLink);
        tempLink.click();
        document.body.removeChild(tempLink);
        // 释放blob URL地址
        window.URL.revokeObjectURL(blobURL)
    }
}

export function set_auth_token() {
    Axios.interceptors.request.use(function (config) {
        // 在发送请求之前做些什么

        if (VueCookies.get('token')) {
            // Axios.defaults.headers.common['Authorization'] = localStorage.getItem('access_token');
            // console.log(config.headers);
            if (VueCookies.get('auth_token')) {
                config.headers.Authorization = VueCookies.get('auth_token')
            } else {
                let token = VueCookies.get('token');
                let username = VueCookies.get('username');
                VueCookies.set("auth_token", Base64.encode(token + ':' + username), 3600 * 24 * 30);
            }
        }
        // 更改加载的样式

        return config;
    }, function (error) {
        // 对请求错误做些什么
        return Promise.reject(error);
    });
}

set_auth_token();

function ErrorMsg(error, load) {
    if (!load) {
        return
    }
    if (error && error.response) {
        switch (error.response.status) {
            case 400:
                error.message = '请求错误(400)';
                break;
            case 401:
                error.message = '未授权，请重新登录(401)';
                break;
            case 403:
                error.message = '拒绝访问(403)';
                break;
            case 404:
                error.message = '请求出错(404)';
                break;
            case 408:
                error.message = '请求超时(408)';
                break;
            case 429:
                error.message = '您的 IP 访问频繁，请稍后再次尝试';
                break;
            case 500:
                error.message = '服务器错误(500)';
                break;
            case 501:
                error.message = '服务未实现(501)';
                break;
            case 502:
                error.message = '网络错误(502)';
                break;
            case 503:
                error.message = '服务不可用(503)';
                break;
            case 504:
                error.message = '网络超时(504)';
                break;
            case 505:
                error.message = 'HTTP版本不受支持(505)';
                break;
            default:
                error.message = `连接出错(${error.response.status}, ${JSON.stringify(error.response.data)})!`;
        }
    } else {
        // eslint-disable-next-line no-console
        console.log(error);
        error.message = '连接服务器失败!';
    }
    if (error.response && error.response.status === 403) {
        router.push({name: 'FirLogin'});
    } else {
        if (error.message === 'Network Error') {
            alert('网络连接失败');
        } else {
            alert(error)
        }
    }
}

function getData(methods, url, params = {}, callBack, load, isCode = false) {

    if (methods === "DELETE") {
        Axios
            .delete(url, {params: params, signal: controller.signal})
            .then(function (response) {
                if (isCode) {
                    callBack(response.data);
                } else {
                    callBack(response.data.data);
                }
            })
            .catch(function (error) {
                ErrorMsg(error, load);
                callBack({"code": -1});
            });

    } else if (methods === "PUT") {
        Axios
            .put(url, params, {signal: controller.signal})
            .then(function (response) {
                if (isCode) {
                    callBack(response.data);
                } else {
                    callBack(response.data.data);
                }
            })
            .catch(function (error) {
                ErrorMsg(error, load);
                callBack({"code": -1});
            });

    } else if (methods === 'POST') {
        Axios
            .post(url, params, {signal: controller.signal})
            .then(function (response) {
                if (isCode) {
                    callBack(response.data);
                } else {
                    callBack(response.data.data);
                }

            })
            .catch(function (error) {
                ErrorMsg(error, load);
                callBack({"code": -1});
            });
    } else if (methods === 'FILE') {
        Axios
            .get(url, {params: params, responseType: 'blob', signal: controller.signal})
            .then(function (response) {
                convertRes2Blob(response)
            })
            .catch(function (error) {
                ErrorMsg(error, load);
                callBack({"code": -1});
            });
    } else {
        Axios
            .get(url, {params: params, signal: controller.signal})
            .then(function (response) {
                callBack(response.data);
            })
            .catch(function (error) {
                ErrorMsg(error, load);
                callBack({"code": -1});
            });
    }
}

/**用户登录 */
export function loginFun(callBack, params, load = true) {
    getData(
        params.methods,
        USERSEVER + '/login',
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/**微信公众号关注登录 */
export function wxLoginFun(callBack, params, load = true) {
    let g_url = 'third.wx.login';
    if (params.methods === 'POST') {
        g_url = 'third.wx.sync'
    }
    getData(
        params.methods,
        USERSEVER + '/' + g_url,
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}


/**微信公众号关注绑定 */
export function wxBindFun(callBack, params, load = true) {
    getData(
        params.methods,
        USERSEVER + '/third.wx.bind',
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/**微信web扫码授权 */
export function wxWebScanFun(callBack, params, load = true) {
    getData(
        params.methods,
        USERSEVER + '/mp.web.sync',
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/**获取验证token */
export function getAuthTokenFun(callBack, params, load = true) {
    getData(
        params.methods,
        USERSEVER + '/auth',
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/**获取信息修改token */
export function getAuthcTokenFun(callBack, params, load = true) {
    getData(
        params.methods,
        USERSEVER + '/authc',
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/**用户注册 */
export function registerFun(callBack, params, load = true) {
    getData(
        params.methods,
        USERSEVER + '/register',
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}


/**用户退出 */
export function logout(callBack, params, load = true) {
    getData(
        'DELETE',
        USERSEVER + '/logout',
        params,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/**api token */
export function apitoken(callBack, params, load = true) {
    getData(
        params.methods,
        USERSEVER + '/token',
        params,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/**用户应用列表 */
export function getapps(callBack, params, load = true) {
    getData(
        'GET',
        USERSEVER + '/apps',
        params,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}


/**app应用操作 */
export function apputils(callBack, params, load = true) {
    getData(
        params.methods,
        USERSEVER + '/apps/' + params.app_id,
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/**release应用操作 */
export function releaseapputils(callBack, params, load = true) {
    getData(
        params.methods,
        USERSEVER + '/appinfos/' + params.app_id + '/' + params.release_id,
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/**应用下载token操作 */
export function appDownloadToken(callBack, params, load = true) {
    getData(
        params.methods,
        USERSEVER + '/download_password/' + params.app_id,
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}


/**根据短链接获取应用信息 */
export function getShortAppinfo(callBack, params, load = true) {
    getData(
        'GET',
        USERSEVER + '/short/' + params.short,
        params,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/**用户app存储配置 */
export function getStorageinfo(callBack, params, load = true) {
    getData(
        params.methods,
        USERSEVER + '/storage',
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/**用户app清理操作 */
export function cleanStorageData(callBack, params, load = true) {
    getData(
        params.methods,
        USERSEVER + '/storage/clean',
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/**用户个人信息 */
export function userinfos(callBack, params, load = true) {
    getData(
        params.methods,
        USERSEVER + '/userinfo',
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

export function getuserpicurl() {
    return USERSEVER + '/userinfo'
}

export function getapppicurl(app_id) {
    return USERSEVER + '/apps/' + app_id
}

export function getuploadurl(domain_name = null) {
    if (domain_name) {
        return domain_name + APIPATH + '/upload'
    } else {
        return USERSEVER + '/upload';
    }
}


/**分析应用并获取app上传token */
export function analyseApps(callBack, params, load = true) {
    getData(
        params.methods,
        USERSEVER + '/analyse',
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}


/**获取下载的url */
export function getdownloadurl(callBack, params, load = true) {
    getData(
        'GET',
        USERSEVER + '/install/' + params.app_id,
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/**上传文件到服务器 */
export function uploadstorage(certinfo, file, successCallback, processCallback) {

    let config = {
        onUploadProgress: function (progressEvent) {
            let total = progressEvent.total;
            let loaded = progressEvent.loaded;
            processCallback(Math.round(loaded * 100 / total))
        },
        headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': VueCookies.get('auth_token'),
        },
    };
    const data = new FormData();
    data.append('file', file);
    data.append('certinfo', JSON.stringify(certinfo));
    Axios.post(certinfo.upload_url, data, config).then(res => {
        // eslint-disable-next-line no-console
        // console.log(res);
        successCallback(res)
    }).catch(err => {
        // eslint-disable-next-line no-console
        console.log(err);
    });

}

/**获取文件上传token */
export function uploadimgs(callBack, params, load = true) {
    getData(
        params.methods,
        USERSEVER + '/upload',
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}


/**获取充值价格信息 */
export function get_package_prices(callBack, params, load = true) {
    getData(
        'GET',
        USERSEVER + '/package_prices',
        params,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/**用户订单 */
export function my_order(callBack, params, load = true) {
    getData(
        params.methods,
        USERSEVER + '/orders',
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/**用户订单支付同步 */
export function order_sync(callBack, params, load = true) {
    getData(
        params.methods,
        USERSEVER + '/orders.sync',
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/**实名认证 */
export function user_certification(callBack, params, load = true) {
    getData(
        params.methods,
        USERSEVER + '/certification',
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/**用户信息修改验证 */
export function changeInfoFun(callBack, params, load = true) {
    getData(
        params.methods,
        USERSEVER + '/change',
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/**用户接收者验证 */
export function NotifyInfoFun(callBack, params, load = true) {
    getData(
        params.methods,
        USERSEVER + '/notify/notify',
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/**用户绑定域名*/
export function domainFun(callBack, params, load = true) {
    getData(
        params.methods,
        USERSEVER + '/cname_domain',
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}


/**微信用户绑定 */
export function wxutils(callBack, params, load = true) {
    getData(
        params.methods,
        USERSEVER + '/twx/info',
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/**访问域名绑定 */
export function domaininfo(callBack, params, load = true) {
    getData(
        params.methods,
        USERSEVER + '/domain_info',
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/**自定义广告 */
export function advertinfo(callBack, params, load = true) {
    getData(
        params.methods,
        USERSEVER + '/advert',
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/**下载码大屏 */
export function qrcodeinfo(callBack, params, load = true) {
    getData(
        params.methods,
        USERSEVER + '/qrcode',
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}


/**应用举报 */
export function appReport(callBack, params, load = true) {
    getData(
        params.methods,
        USERSEVER + '/report',
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/**消息接收人配置 */
export function notifyReceiverInfo(callBack, params, load = true) {
    getData(
        params.methods,
        USERSEVER + '/notify/receiver',
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/**消息配置 */
export function notifyConfigInfo(callBack, params, load = true) {
    getData(
        params.methods,
        USERSEVER + '/notify/config',
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/** 超级签名************************************************相关api */

let SIGNSEVER = DOMAIN + '/api/v1/fir/xsign';

/** 超级签名--检测该账户是否可开启超级签名 */
export function checkCanSign(callBack, params, load = false) {
    getData(
        params.methods,
        SIGNSEVER + '/cansign',
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/** 苹果签名应用操作 */
export function appSignInfo(callBack, params, load = true) {
    getData(
        params.methods,
        SIGNSEVER + '/signinfo/' + params.app_id,
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/**签名账单 */
export function DeviceBillInfo(callBack, params, load = true) {
    getData(
        params.methods,
        SIGNSEVER + '/bill',
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/**设备流转账单 */
export function DeviceTransferBillInfo(callBack, params, load = true) {
    getData(
        params.methods,
        SIGNSEVER + '/devicebill',
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/**签名下载排行 */
export function DeviceRankInfo(callBack, params, load = true) {
    getData(
        params.methods,
        SIGNSEVER + '/rank',
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/**开发绑定应用*/
export function developerBindAppFun(callBack, params, load = true) {
    getData(
        params.methods,
        SIGNSEVER + '/bind',
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}


/**超级签名 苹果开发者信息 */
export function iosdeveloper(callBack, params, load = true) {
    getData(
        params.methods,
        SIGNSEVER + '/developer',
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/**超级签名 设备消耗信息 */
export function iosdevices(callBack, params, load = true) {
    getData(
        params.methods,
        SIGNSEVER + '/devices',
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/**超级签名 设备udid信息 */
export function iosdevicesudid(callBack, params, load = true) {
    // eslint-disable-next-line no-console
    getData(
        params.methods,
        SIGNSEVER + '/udid',
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/**超级签名 苹果开发设备udid信息 */
export function iosudevices(callBack, params, load = true) {
    // eslint-disable-next-line no-console
    getData(
        params.methods,
        SIGNSEVER + '/udevices',
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/**签名证书 */
export function developercert(callBack, params, load = true) {
    getData(
        params.methods,
        SIGNSEVER + '/cert',
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/**签名证书 */
export function signoperatemessage(callBack, params, load = true) {
    getData(
        params.methods,
        SIGNSEVER + '/message',
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}

/**获取签名任务状态 */
export function gettask(callBack, params, load = true) {
    getData(
        params.methods,
        SIGNSEVER + '/task/' + params.short,
        params.data,
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}


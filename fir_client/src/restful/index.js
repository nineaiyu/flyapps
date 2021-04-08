import Axios from 'axios'
import VueCookies from 'vue-cookies'
import router from "../router";

// const https = require('https');
const Base64 = require('js-base64').Base64;
Axios.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded';
Axios.defaults.withCredentials = true;
// Axios.defaults.httpsAgent = new https.Agent({
//     keepAlive: true
// });


// const DOMAIN = 'https://fly.harmonygames.cn';
const DOMAIN = window.g.baseUrl;
// const DOMAIN = 'https://testapp.harmonygames.cn';
// const DOMAIN = 'http://172.16.133.34:8000';
const APIPATH = '/api/v1/fir/server';
let USERSEVER = DOMAIN + APIPATH;


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

function ErrorMsg(error) {
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
            .delete(url, {params: params})
            .then(function (response) {
                if (isCode) {
                    callBack(response.data);
                } else {
                    callBack(response.data.data);
                }
            })
            .catch(function (error) {
                ErrorMsg(error);
                callBack({"code": -1});
            });

    } else if (methods === "PUT") {
        Axios
            .put(url, params)
            .then(function (response) {
                if (isCode) {
                    callBack(response.data);
                } else {
                    callBack(response.data.data);
                }
            })
            .catch(function (error) {
                ErrorMsg(error);
                callBack({"code": -1});
            });

    } else if (methods === 'POST') {
        Axios
            .post(url, params)
            .then(function (response) {
                if (isCode) {
                    callBack(response.data);
                } else {
                    callBack(response.data.data);
                }

            })
            .catch(function (error) {
                ErrorMsg(error);
                callBack({"code": -1});
            });
    } else {
        Axios
            .get(url, {params: params})
            .then(function (response) {
                callBack(response.data);
            })
            .catch(function (error) {
                ErrorMsg(error);
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

/**超级签名 苹果开发者信息 */
export function iosdeveloper(callBack, params, load = true) {
    getData(
        params.methods,
        USERSEVER + '/supersign/developer',
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
        USERSEVER + '/supersign/devices',
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
        USERSEVER + '/supersign/udid',
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
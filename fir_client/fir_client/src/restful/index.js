import Axios from 'axios'
import VueCookies from 'vue-cookies'

import router from "../router";

const https = require('https');
const Base64 = require('js-base64').Base64;
Axios.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded';
Axios.defaults.withCredentials = true;
Axios.defaults.httpsAgent = new https.Agent({
    keepAlive: true
});

// Axios.defaults.baseURL='';
// const USERSEVER = 'https://fly.dvcloud.xin/api/v1/fir/server';

const USERSEVER = 'http://192.168.1.112:8000/api/v1/fir/server';


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
                VueCookies.set("auth_token", Base64.encode(token + ':' + username));
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

function getData(PostType = true, url, params = {}, callBack, load, isCode = false) {

    let methods = PostType;
    if (methods === "DELETE") {
        Axios
            .delete(url, params)
            .then(function (response) {
                if (isCode) {
                    callBack(response.data);
                } else {
                    callBack(response.data.data);
                }
            })
            .catch(function (error) {
                // eslint-disable-next-line no-console
                console.log(error, error.response);
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
                            error.message = `连接出错(${error.response.status})!`;
                    }
                } else {
                    error.message = '连接服务器失败!';
                }
                if (error.message === 'Network Error') {
                    alert('网络连接失败');
                } else {
                    alert(error)
                }
                callBack(null);
            });

    }
    else  if (methods === "PUT") {
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
                // eslint-disable-next-line no-console
                console.log(error, error.response);
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
                            error.message = `连接出错(${error.response.status})!`;
                    }
                } else {
                    error.message = '连接服务器失败!';
                }
                if (error.message === 'Network Error') {
                    alert('网络连接失败');
                } else {
                    alert(error)
                }
                callBack(null);
            });

    }


   else if (PostType===true) {
        Axios
            .post(url, params)
            .then(function (response) {
                let type = response.data.type;
                if (isCode) {
                    callBack(response.data);
                } else {
                    callBack(response.data.data);
                }
                let x = '';
                switch (type) {
                    case 8001:
                        x = "服务器内部错误";
                        break;
                    case 8002:
                        x = "错误密码";
                        break;
                    case 8004:
                        x = "验证码错误";
                        break;
                    case 8005:
                        x = "没有这个玩家信息";
                        break;
                    case 8006:
                        x = "请重新登录账号";
                        break;
                    case 8009:
                        x = "没有权限";
                        break;
                    case 8011:
                        x = "账号被冻结";
                        break;
                    case 8013:
                        x = "用户名已存在";
                        break;
                    case 9001:
                        x = "系统繁忙";
                        break;
                    case 9007:
                        x = "错误的参数";
                        break;

                    case 20009:
                        x = "上传文件失败";
                        break;
                }
                if (x !== '') {
                    alert(x)
                }
            })
            .catch(function (error) {
                // eslint-disable-next-line no-console
                console.log(error, error.response);
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
                            error.message = `连接出错(${error.response.status})!`;
                    }
                } else {
                    error.message = '连接服务器失败!';
                }
                if (error.message === 'Network Error') {
                    alert('网络连接失败');
                } else {
                    alert(error)
                }
                callBack(null);
            });
    } else {
        // console.log(JSON.stringify(params) + "参数")
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
        Axios
            .get(url, params)
            .then(function (response) {
                let type = response.data.type;
                callBack(response.data);
                let x = '';
                switch (type) {
                    case 8001:
                        x = "服务器内部错误";
                        break;
                    case 8002:
                        x = "错误密码";
                        break;
                    case 8004:
                        x = "验证码错误";
                        break;
                    case 8005:
                        x = "没有这个玩家信息";
                        break;
                    case 8006:
                        x = "请重新登录账号";
                        break;
                    case 8009:
                        x = "没有权限";
                        break;
                    case 8011:
                        x = "账号被冻结";
                        break;
                    case 8013:
                        x = "用户名已存在";
                        break;
                    case 9001:
                        x = "系统繁忙";
                        break;
                    case 9007:
                        x = "错误的参数";
                        break;

                    case 20009:
                        x = "上传文件失败";
                        break;
                }
                if (x !== '') {
                    alert(x)
                }
            })
            .catch(function (error) {


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
                            error.message = `连接出错(${error.response.status})!`;
                    }
                } else {
                    error.message = '连接服务器失败!';
                }
                if (error.message === 'Network Error') {
                    alert('网络连接失败')
                } else {


                    if (error.response.status === 403) {

                        router.push({name: 'FirLogin'})
                    } else {
                        alert(error.message);
                    }

                }
                callBack(null);
            });
    }
}

/**用户登录 */
export function loginFun(callBack, params, load = true) {
    getData(
        true,
        USERSEVER + '/login',
        params,
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


/**用户应用列表 */
export function getapps(callBack, params, load = true) {
    getData(
        false,
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

/**用户应用详情 */
export function getappinfos(callBack, params, load = true) {
    getData(
        false,
        USERSEVER + '/apps/' + params.app_id,
        {},
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}


/**删除应用 */
export function deleteapp(callBack, params, load = true) {
    getData(
        "DELETE",
        USERSEVER + '/apps/' + params.app_id,
        {},
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}


/**删除release应用 */
export function deletereleaseapp(callBack, params, load = true) {
    getData(
        "DELETE",
        USERSEVER + '/appinfos/' + params.app_id + '/' + params.release_id,
        {},
        data => {
            callBack(data);
        },
        load,
        true,
        true
    );
}


/**更新app应用 */
export function updateapp(callBack, params, load = true) {
    getData(
        "PUT",
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


/**更新release应用 */
export function updatereleaseapp(callBack, params, load = true) {
    getData(
        "PUT",
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


/**用户应用详情 */
export function getapptimeline(callBack, params, load = true) {
    getData(
        params.methods,
        USERSEVER + '/appinfos/' + params.app_id + '/' + params.action,
        {},
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
        false,
        USERSEVER + '/short/' + params.short ,
        params,
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
    return USERSEVER+ '/userinfo'
}
export function getapppicurl(app_id) {
    return USERSEVER + '/apps/' + app_id
}

export function getuploadurl() {
    return USERSEVER + '/upload'
}
export function getplisturl() {
    return USERSEVER + '/download'
}


/**分析应用并获取app上传token */
export function analyseApps(callBack, params, load = true) {
    getData(
        params.methods,
        USERSEVER + '/analyse' ,
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
        false,
        USERSEVER + '/install/'+params.app_id ,
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
export function uploadstorage(certinfo,file,successCallback,processCallback) {

    let config = {
        onUploadProgress: function (progressEvent) {
            let total=progressEvent.total;
            let loaded = progressEvent.loaded;
            processCallback(Math.round(loaded*100/total))
        },
        headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization':VueCookies.get('auth_token'),
        },
    };
    const data = new FormData();
    data.append('file', file);
    data.append('certinfo',JSON.stringify(certinfo));
    Axios.post(certinfo.upload_url, data, config).then(res => {
        // eslint-disable-next-line no-console
        console.log(res);
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


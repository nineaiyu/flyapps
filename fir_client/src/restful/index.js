import Axios from 'axios'
import VueCookies from 'vue-cookies'

const https = require('https');
const Base64 = require('js-base64').Base64;
Axios.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded';
Axios.defaults.withCredentials = true;
Axios.defaults.httpsAgent = new https.Agent({
    keepAlive: true
});

// Axios.defaults.baseURL='';
const USERSEVER = 'https://fly.dvcloud.xin/api/v1/fir/server';

// const USERSEVER = 'http://192.168.1.112:8000/api/v1/fir/server';


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

function getData(methods = true, url, params = {}, callBack, load, isCode = false) {

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

                callBack(null);
            });

    }


   else if (methods === 'POST') {
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
                // eslint-disable-next-line no-console
                console.log(error, error.response);
                callBack(null);
            });
    } else  {
        Axios
            .get(url, {params: params})
            .then(function (response) {
                callBack(response.data);
            })
            .catch(function (error) {
                // eslint-disable-next-line no-console
                console.log(error, error.response);
                callBack(null);
            });
    }
}

/**用户登录 */
export function loginFun(callBack, params, load = true) {
    getData(
        'POST',
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

/**用户应用详情 */
export function getappinfos(callBack, params, load = true) {
    getData(
        'GET',
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
        'GET',
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
        'GET',
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

/**用户app存储配置 */
export function getStorageinfo(callBack, params, load = true) {
    getData(
        params.methods,
        USERSEVER + '/storage' ,
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
        'GET',
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


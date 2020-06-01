import Axios from 'axios'
const https = require('https');
Axios.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded';
Axios.defaults.withCredentials = true;
Axios.defaults.httpsAgent = new https.Agent({
    keepAlive: true
});

const DOMAIN = 'https://fly.harmonygames.cn';
const APIPATH='/api/v1/fir/server';
let USERSEVER = DOMAIN+APIPATH;


function getData(url, params = {}, callBack) {


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
            callBack(response.data);
            let x = '';
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
            }

            callBack({"code":-1});
        });
}



/**根据短链接获取应用信息 */
export function getShortAppinfo(callBack, params) {
    getData(
        USERSEVER + '/short/' + params.short ,
        params,
        data => {
            callBack(data);
        },
    );
}


/**获取下载的url */
export function getdownloadurl(callBack, params) {
    getData(
        USERSEVER + '/install/'+params.app_id ,
        params.data,
        data => {
            callBack(data);
        },
    );
}

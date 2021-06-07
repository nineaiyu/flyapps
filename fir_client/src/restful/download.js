import Axios from 'axios'

Axios.defaults.withCredentials = true;

const DOMAIN = process.env.base_env.baseUrl;
const APIPATH = '/api/v1/fir/server';
let USERSEVER = DOMAIN + APIPATH;


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
            callBack({"code": -1});
        });
}


/**根据短链接获取应用信息 */
export function getShortAppinfo(callBack, params) {
    getData(
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
        USERSEVER + '/install/' + params.app_id,
        params.data,
        data => {
            callBack(data);
        },
    );
}

/**获取签名任务状态 */
export function gettask(callBack, params) {
    getData(
        USERSEVER + '/task/' + params.short,
        params.data,
        data => {
            callBack(data);
        },
    );
}

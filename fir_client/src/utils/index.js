//滚动条在Y轴上的滚动距离

export function getScrollTop() {
    let scrollTop = 0, bodyScrollTop = 0, documentScrollTop = 0;
    if (document.body) {
        bodyScrollTop = document.body.scrollTop;
    }
    if (document.documentElement) {
        documentScrollTop = document.documentElement.scrollTop;
    }
    scrollTop = (bodyScrollTop - documentScrollTop > 0) ? bodyScrollTop : documentScrollTop;
    // return Math.ceil(scrollTop);
    return scrollTop;
}


//文档的总高度
export function getScrollHeight() {
    let scrollHeight = 0, bodyScrollHeight = 0, documentScrollHeight = 0;
    if (document.body) {
        bodyScrollHeight = document.body.scrollHeight;
    }
    if (document.documentElement) {
        documentScrollHeight = document.documentElement.scrollHeight;
    }
    scrollHeight = (bodyScrollHeight - documentScrollHeight > 0) ? bodyScrollHeight : documentScrollHeight;
    return scrollHeight;
}


//浏览器视口的高度
export function getWindowHeight() {
    let windowHeight = 0;
    if (document.compatMode === "CSS1Compat") {
        windowHeight = document.documentElement.clientHeight;
    } else {
        windowHeight = document.body.clientHeight;
    }
    return windowHeight;
}

export function getappinfo(file, successcallback, errcallback) {
    const AppInfoParser = require('app-info-parser');
    const parser = new AppInfoParser(file);
    let analyseappinfo = {};
    parser.parse().then(result => {
        analyseappinfo.icon = result.icon;
        analyseappinfo.filename = file.name;
        analyseappinfo.filesize = file.size;
        if (result.CFBundleDisplayName) {
            analyseappinfo.appname = result.CFBundleDisplayName;
            analyseappinfo.bundleid = result.CFBundleIdentifier;
            analyseappinfo.version = result.CFBundleShortVersionString;
            analyseappinfo.buildversion = result.CFBundleVersion;
            analyseappinfo.miniosversion = result.MinimumOSVersion;
            if (result.mobileProvision.ProvisionedDevices) {
                analyseappinfo.release_type = 'Adhoc';
                analyseappinfo.release_type_id = 1;
                analyseappinfo.udid = result.mobileProvision.ProvisionedDevices;
            } else {
                analyseappinfo.distribution_name = result.mobileProvision.Name + ": " + result.mobileProvision.TeamName;
                analyseappinfo.release_type = 'Inhouse';
                analyseappinfo.release_type_id = 2;
                analyseappinfo.udid = [];
            }
            analyseappinfo.type = 'iOS';
        } else {
            analyseappinfo.appname = result.application.label[0];
            analyseappinfo.bundleid = result.package;
            analyseappinfo.version = result.versionName;
            analyseappinfo.buildversion = result.versionCode;
            analyseappinfo.miniosversion = result.usesSdk.minSdkVersion;
            analyseappinfo.type = 'Android';
            analyseappinfo.release_type = 'Android';
            analyseappinfo.release_type_id = 0;

        }
        successcallback(analyseappinfo)

    }).catch(err => {
        errcallback(err);
    });
}

export function uploadqiniuoss(file, certinfo, app, successcallback, processcallback) {
    // let app = this;
    // let file=this.currentfile;
    let observer = {
        next(res) {
            processcallback(Math.round(res.total.percent));
        },
        error(err) {
            // eslint-disable-next-line no-console
            console.log(err);
            app.$message({
                message: file.name + '上传失败，请刷新页面重试',
                type: 'error',
                duration: 0
            });
        },
        complete(res) {
            // eslint-disable-next-line no-console
            // console.log(res);
            successcallback(res);
        }
    };
    let putExtra = {
        fname: file.name,
        params: {},
        // mimeType: ["image/png"]
    };
    let config = {};
    let observable = app.qiniu.upload(file, certinfo.upload_key, certinfo.upload_token, putExtra, config);
    // eslint-disable-next-line no-unused-vars
    let subscription = observable.subscribe(observer) // 上传开始
    // subscription.unsubscribe() // 上传取消
}

export function dataURLtoFile(dataurl, filename) {//将base64转换为文件
    let arr = dataurl.split(','), mime = arr[0].match(/:(.*?);/)[1],
        bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
    while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
    }
    return new File([u8arr], filename, {type: mime});
}

export function uploadaliyunoss(file, certinfo, app, successcallback, processcallback) {
    let token = certinfo.upload_token;
    let client = new app.oss({
        endpoint: token.endpoint,
        accessKeyId: token.access_key_id,
        accessKeySecret: token.access_key_secret,
        stsToken: token.security_token,
        bucket: token.bucket
    });

    // eslint-disable-next-line no-unused-vars
    let currentCheckpoint;
    const progress = async function progress(p, checkpoint) {
        currentCheckpoint = checkpoint;
        // eslint-disable-next-line no-console
        // console.log(Math.floor(p * 100));
        // eslint-disable-next-line no-console
        // console.log(checkpoint);
        processcallback(Math.floor(p * 100));

    };
    const options = {
        progress,
        partSize: 1024 * 1024 / 4,
        // meta: {
        //     year: 2017,
        //     people: 'test',
        // },
    };
    client.multipartUpload(certinfo.upload_key, file, options).then((res) => {
        // eslint-disable-next-line no-console
        // console.log('upload success: %j', res);
        successcallback(res);
        currentCheckpoint = null;
    }).catch((err) => {
        // eslint-disable-next-line no-console
        console.error(err);
        app.$message({
            message: file.name + '上传失败，请刷新页面重试',
            type: 'error',
            duration: 0
        });
    });
}


import {uploadstorage} from '../restful'

export function uploadlocalstorage(file, certinfo, app, successcallback, processcallback) {
    uploadstorage(certinfo, file, successcallback, processcallback)

}

export function removeAaary(_arr, _obj) {
    var length = _arr.length;
    for (var i = 0; i < length; i++) {
        if (_arr[i] == _obj) {
            if (i == 0) {
                _arr.shift(); //删除并返回数组的第一个元素
                return _arr;
            } else if (i == length - 1) {
                _arr.pop();  //删除并返回数组的最后一个元素
                return _arr;
            } else {
                _arr.splice(i, 1); //删除下标为i的元素
                return _arr;
            }
        }
    }
}

//深拷贝-字段不能为null
// export function deepCopy(source) {
//     let result = {};
//     for (let key in source) {
//         result[key] = typeof source[key] === 'object' ? deepCopy(source[key]) : source[key];
//     }
//     return result;
// }
//
// //深拷贝-只有json
// export function deepCopyJson(source) {
//     return JSON.parse(JSON.stringify(source))
// }

export function IsNum(s) {
    if (s != null) {
        var r, re;
        re = /\d*/i; //\d表示数字,*表示匹配多个数字
        r = s.match(re);
        return (r == s) ? true : false;
    }
    return false;
}

function getType(x) {
    if (x) {
        if (x.constructor.toString().indexOf("Array") > -1) {
            return 'array'
        } else if (x.constructor.toString().indexOf("Number") > -1) {
            return 'number'
        } else if (x.constructor.toString().indexOf("String") > -1) {
            return 'string'
        } else if (x.constructor.toString().indexOf("Object") > -1) {
            return 'object'
        } else {
            return x.constructor.toString()
        }
    } else {
        return x
    }

}

//深拷贝
export function deepCopy(data) {
    let type = getType(data);
    let obj;
    if (type === 'array') {
        obj = [];
    } else if (type === 'object') {
        obj = {};
    } else {
        //不再具有下一层次
        return data;
    }
    if (type === 'array') {
        for (let i = 0, len = data.length; i < len; i++) {
            obj.push(deepCopy(data[i]));
        }
    } else if (type === 'object') {
        for (let key in data) {
            obj[key] = deepCopy(data[key]);
        }
    }
    return obj;
}

export function checkEmail(email) {
    let re = /^(\w-*\.*)+@(\w-?)+(\.\w{2,})+$/;
    return re.test(email);
}

export function checkphone(email) {
    let re = /^1\d{10}$/;
    return re.test(email);
}

export function ImgToBase64(url, callback) {
    let Img = new Image(),
        dataURL = '';
    Img.src = url + '?v=' + Math.random();
    Img.crossOrigin = 'Anonymous';
    Img.onload = function () {
        let canvas = document.createElement('canvas'),
            width = Img.width,
            height = Img.height;
        canvas.width = width;
        canvas.height = height;
        canvas.getContext('2d').drawImage(Img, 0, 0, width, height);
        dataURL = canvas.toDataURL('image/jpeg',);
        return callback ? callback(dataURL) : null;
    };
}

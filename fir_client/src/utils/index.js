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


import {getuploadurl, loginFun, uploadimgs, uploadstorage} from '../restful'

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

export function geetest(self, params, callback) {
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
                    //your code
                }).onSuccess(() => {
                    params.geetest = captchaObj.getValidate();
                    callback(params);
                }).onError(() => {
                    captchaObj.destroy();
                });
            });

        } else {

            self.$message({
                message: res.msg,
                type: 'error'
            });
        }
    }, {
        "methods": "PUT",
        "data": {user_id: self.form.email}
    });
}

export function format_money(s, n = 2) {
    n = n > 0 && n <= 20 ? n : -1;
    s = parseFloat((s + "").replace(/[^\d\\.-]/g, "")).toFixed(n) + "";
    let l = s.split(".")[0].split("").reverse();
    let r = s.split(".")[1];
    let t = "";
    for (let i = 0; i < l.length; i++) {
        t += l[i] + ((i + 1) % 3 === 0 && (i + 1) !== l.length ? "," : "");
    }
    let new_format_money = t.split("").reverse().join("");
    if (n !== 19) {
        new_format_money += "." + r
    }
    return new_format_money
}

export function show_beautpic(father, canvas, nb = 666) {
    let ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    ctx.lineWidth = .3;
    ctx.strokeStyle = (new Color(150)).style;

    father.mousePosition = {
        x: 30 * canvas.width / 100,
        y: 30 * canvas.height / 100
    };

    let dots = {
        nb: nb,
        distance: 100,
        d_radius: 150,
        array: []
    };

    function colorValue(min) {
        return Math.floor(Math.random() * 255 + min);
    }

    function createColorStyle(r, g, b) {
        return 'rgba(' + r + ',' + g + ',' + b + ', 0.8)';
    }

    function mixComponents(comp1, weight1, comp2, weight2) {
        return (comp1 * weight1 + comp2 * weight2) / (weight1 + weight2);
    }

    function averageColorStyles(dot1, dot2) {
        let color1 = dot1.color,
            color2 = dot2.color;

        let r = mixComponents(color1.r, dot1.radius, color2.r, dot2.radius),
            g = mixComponents(color1.g, dot1.radius, color2.g, dot2.radius),
            b = mixComponents(color1.b, dot1.radius, color2.b, dot2.radius);
        return createColorStyle(Math.floor(r), Math.floor(g), Math.floor(b));
    }

    function Color(min) {
        min = min || 0;
        this.r = colorValue(min);
        this.g = colorValue(min);
        this.b = colorValue(min);
        this.style = createColorStyle(this.r, this.g, this.b);
    }

    function Dot() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;

        this.vx = -.5 + Math.random();
        this.vy = -.5 + Math.random();

        this.radius = Math.random() * 2;

        this.color = new Color();
    }

    Dot.prototype = {
        draw: function () {
            ctx.beginPath();
            ctx.fillStyle = this.color.style;
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2, false);
            ctx.fill();
        }
    };

    function createDots() {
        for (let i = 0; i < dots.nb; i++) {
            dots.array.push(new Dot());
        }
    }

    function moveDots() {
        for (let i = 0; i < dots.nb; i++) {

            let dot = dots.array[i];

            if (dot.y < 0 || dot.y > canvas.height) {
                // dot.vx = dot.vx;
                dot.vy = -dot.vy;
            } else if (dot.x < 0 || dot.x > canvas.width) {
                dot.vx = -dot.vx;
                // dot.vy = dot.vy;
            }
            dot.x += dot.vx;
            dot.y += dot.vy;
        }
    }

    function connectDots() {
        for (let i = 0; i < dots.nb * 0.3; i++) {
            for (let j = 0; j < dots.nb * 0.3; j++) {
                let i_dot = dots.array[i];
                let j_dot = dots.array[j];

                if ((i_dot.x - j_dot.x) < dots.distance && (i_dot.y - j_dot.y) < dots.distance && (i_dot.x - j_dot.x) > -dots.distance && (i_dot.y - j_dot.y) > -dots.distance) {
                    if ((i_dot.x - father.mousePosition.x) < dots.d_radius && (i_dot.y - father.mousePosition.y) < dots.d_radius && (i_dot.x - father.mousePosition.x) > -dots.d_radius && (i_dot.y - father.mousePosition.y) > -dots.d_radius) {
                        ctx.beginPath();
                        ctx.strokeStyle = averageColorStyles(i_dot, j_dot);
                        ctx.moveTo(i_dot.x, i_dot.y);
                        ctx.lineTo(j_dot.x, j_dot.y);
                        ctx.stroke();
                        ctx.closePath();
                    }
                }
            }
        }
    }

    function drawDots() {
        for (let i = 0; i < dots.nb; i++) {
            let dot = dots.array[i];
            dot.draw();
        }
    }

    function animateDots() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        moveDots();
        connectDots();
        drawDots();

        requestAnimationFrame(animateDots);
    }

    createDots();
    requestAnimationFrame(animateDots);
}


function updateimgs(fthis, certinfo, callabck) {
    uploadimgs(data => {
        if (data.code === 1000) {
            fthis.$message.success('上传成功');
            callabck()
        } else {
            fthis.$message.error('更新失败: ' + data.msg);
        }
    }, {'methods': 'PUT', 'data': {'certinfo': certinfo}});
}

function uploadtostorage(fthis, file, certinfo, callabck) {

    if (certinfo.storage === 1) {
        // eslint-disable-next-line no-unused-vars,no-unreachable
        uploadqiniuoss(file, certinfo, this, res => {
            updateimgs(fthis, certinfo, callabck);

        }, process => {
            fthis.uploadprocess = process;
        })
    } else if (certinfo.storage === 2) {
        // eslint-disable-next-line no-unused-vars
        uploadaliyunoss(file, certinfo, this, res => {
            updateimgs(fthis, certinfo, callabck);
        }, process => {
            fthis.uploadprocess = process;
        });

    } else {
        //本地
        if (certinfo.domain_name) {
            certinfo.upload_url = getuploadurl(certinfo.domain_name)
        } else {
            certinfo.upload_url = getuploadurl();
        }
        // eslint-disable-next-line no-unused-vars,no-unreachable
        uploadlocalstorage(file, certinfo, this, res => {
            updateimgs(fthis, certinfo, callabck);
        }, process => {
            fthis.uploadprocess = process;
        })
    }

}

/**
 * @return {boolean}
 */
export function AvatarUploadUtils(fthis, file, params, callabck) {
    const isLt2M = file.size / 1024 / 1024 < 2;
    if (file.type === 'image/jpeg' || file.type === 'image/png' || file.type === 'image/jpg') {
        if (isLt2M) {
            uploadimgs(data => {
                if (data.code === 1000) {
                    // eslint-disable-next-line no-console
                    // console.log(data.data);
                    let certinfo = data.data;
                    certinfo.ext = params.ext;
                    uploadtostorage(fthis, file, certinfo, callabck);
                } else {
                    fthis.$message.error('参数有误');
                }
            }, {
                'methods': 'GET',
                'data': params
            });

            return false;
        } else {
            fthis.$message.error('上传头像图片大小不能超过 2MB!');

        }
    } else {
        fthis.$message.error('上传头像图片只能是 JPG/PNG/JPEG 格式!');

    }
    return false;

}
//滚动条在Y轴上的滚动距离

import {geetestbase} from "@/utils/base/utils";
import {getuploadurl, loginFun, uploadimgs, uploadstorage, userinfos} from '@/restful'

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
        if (analyseappinfo.icon === '' || analyseappinfo.icon === null) {
            analyseappinfo.icon = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMgAAADICAMAAACahl6sAAABNVBMVEXzpkDzpkHzp0Lzp0PzqETzqUjzqkjzqknzrE7zrU/0rVD0r1P0r1T0sFX0sFb0sFf0sVf0sVj0sVn0slr1tWD1tWH1tmL1tmP1t2T1umz1u231u2/2vG/2vHD2vXH2wHj2wXr2wXv2wnz2wn32wn72w373xYL3xYT3xoT3xoX3x4f3x4j3yIn3yIr3yYv3yYz3yo34zJL4zJP4zZT4zpb4z5n50p/506H506L51KL51KP516v52Kz52a762q/62rD62rH63rn63rr637v637z64L375Mb75cj75cn75sn75sr86tP869T869X87Nb87Nf879798N/98OD98eH98eL98uP98uT98+X98+b99On99er99ev99uz++PH++fL++fP++/f++/j+/Pn+/fz+/v3+/v7///+pZW9PAAAC/0lEQVR4AezBgQAAAACAoP2pF6kCAAAAAAAAAAAAAABm376aWjmiIAD3XnEvWQQTMGACyIGAAzkHkMDkIDAGJCGxov//T3ChObWlAVRlrVQ1e8r+3qb0dB521bPT85/R/tPcd4B+S0WyuAT1fmPJr1DOu2PJnQfdEhQJ6HZJcQnVRhgYgWYnDJxAsQGWGYBeKZZJQa1un2X8bmi1S8sulGp5oeWlBTqt8511qNT4TOPqisZzIzRapJiaoliEQg1PNB5isQcaTw3QZ45iHpinmIM6XppG9ivwNUsj7UGbSYrlt9UyxSS0uaCRb3pbNeVpXECZYYpNs96kGIYuxzT8DrPu8GkcQ5V+in2IfYp+aJKk6IXopUhCkS6fxiEChzT8LuixTTGIwCDFtqL8XqBxhjJnNAp60vwaxRjKjFGsQYlvORo3sNzQyH3Tlt+nYZlWluYbHmk8xmCJBT/oSPMzFAt4Z4FiBhqkKz4KwcOThgLjFCv4YIViHNF3TqPQjA+aCzTOEXlDFFv4xBbFEKLuiIbfiU90+jSOEHF9FAf41AFFH6KjLZlhHWVS7Y7myLLOcm4mSbLuUnAhw7rL/D9ILVKsuyRcaM+xzrJtcDNJqr6v36TM4dxsxfxeIc3PIpqsrWyIrbCG/F45zSvL75XTvLb8rijNH1XxSbQrSPPq8ruCNC8Oqjo26LfHdi/01u9PeyMZHfbjG/7V4FpTvtoX6rl1WBoZKxQT+Jcm7L/PiAhRCLAKBZFhx8DwEdO1EKUZq3QD98IffFjHKFFxHRTLQhXTrhERYyGrfuv2UaN7p0H5MmR58xSRMEixgyrtUHyPKDgMXVDutgoSrvW80kiF/zT22gP39moo8Q9Q7MG5uE/jpJZrGX4crm1Q/FDTRZkNuHZP47K2q0t/w7EvRRqJ2i6TFb/Asb9YcushFO+WJfdRuTA5ipBGWfI7XPNWi2RhHqH9kSeLqx7ci//yYytq0Jr4OY5/2oMDGQAAAIBB/tb3+KoLAAAAAAAAAAAAAAAg6P6/9f2bMMkAAAAASUVORK5CYII="
        }
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

function get_file_type(upload_key) {
    if (upload_key) {
        const key_list = upload_key.split('.');
        if (key_list.length > 2) {
            return key_list[key_list.length - 2]
        }
    }
}

function get_filename(app_info, upload_key) {
    if (app_info) {
        let app_type = app_info.type;
        if (app_type === 'iOS' || app_type === 'Android') {
            return app_info.appname + '-' + app_info.version + '-' + app_info.short + '.' + get_file_type(upload_key)
        }
    }
}

export function uploadaliyunoss(file, certinfo, app, successcallback, processcallback) {
    let token = certinfo.upload_token;
    let uploadFileClient = new app.oss({
        endpoint: token.endpoint,
        accessKeyId: token.access_key_id,
        accessKeySecret: token.access_key_secret,
        stsToken: token.security_token,
        bucket: token.bucket
    });


    let retryCount = 0;
    let partSize = 1024 * 1024;

    let f_count = Math.floor(file.size / partSize);

    if (f_count > 200) {
        f_count = Math.floor(f_count * 0.3)
    } else {
        f_count = 60
    }
    let retryCountMax = 5 + f_count;
    let currentCheckpoint;
    const progress = async function progress(p, checkpoint) {
        currentCheckpoint = checkpoint;
        // eslint-disable-next-line no-console
        // console.log(Math.floor(p * 100));
        // eslint-disable-next-line no-console
        // console.log(checkpoint);
        processcallback(Math.floor(p * 100));

    };

    const uploadFile = function uploadFile(client) {
        if (!uploadFileClient || Object.keys(uploadFileClient).length === 0) {
            uploadFileClient = client;
        }

        let options = {
            progress,
            parallel: 10,
            partSize: 1024 * 1024,
            timeout: 600000,
        };
        let filename = get_filename(certinfo.app_info, certinfo.upload_key);
        if (filename) {
            options['headers'] = {
                'Content-Disposition': 'attachment; filename="' + encodeURIComponent(filename) + '"',
                'Cache-Control': ''
            }
        } else {
            options['headers'] = {
                'Cache-Control': ''
            }
        }

        if (currentCheckpoint) {
            options.checkpoint = currentCheckpoint;
        }
        return uploadFileClient.multipartUpload(certinfo.upload_key, file, options).then((res) => {
            successcallback(res);
            currentCheckpoint = null;
        }).catch((err) => {
            // eslint-disable-next-line no-console
            console.error(err);

            //retry
            if (retryCount < retryCountMax) {
                retryCount++;
                // eslint-disable-next-line no-console
                console.error("retryCount : " + retryCount);
                // eslint-disable-next-line no-unused-vars
                setTimeout(_ => {
                    uploadFile('')
                }, 1000);
            } else {
                app.$message({
                    message: file.name + ' 重试了' + retryCount + '次，还是上传失败了，请刷新页面重试',
                    type: 'error',
                    duration: 0
                });
            }
        });
    };
    uploadFile(uploadFileClient)
}


export function uploadlocalstorage(file, certinfo, app, successcallback, processcallback) {
    uploadstorage(certinfo, file, successcallback, processcallback)

}

export function removeAaary(_arr, _obj) {
    let length = _arr.length;
    for (let i = 0; i < length; i++) {
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

export function geetest(self, uid, params, callback) {
    const loading = self.$loading({
        lock: true,
        text: 'Loading',
        spinner: 'el-icon-loading',
    });
    return geetestbase(self, loginFun, uid, params, callback, res => {
        self.$message({
            message: res.msg,
            type: 'error'
        });
        // eslint-disable-next-line no-unused-vars
    }, _ => {
        loading.close()
    })
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

export function show_beautpic(father, canvas, nb = 666, sp = 0.3) {
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
        d_radius: 180,
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
        for (let i = 0; i < dots.nb * sp; i++) {
            for (let j = 0; j < dots.nb * sp; j++) {
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
        uploadqiniuoss(file, certinfo, fthis, res => {
            updateimgs(fthis, certinfo, callabck);

        }, process => {
            fthis.uploadprocess = process;
        })
    } else if (certinfo.storage === 2) {
        // eslint-disable-next-line no-unused-vars
        uploadaliyunoss(file, certinfo, fthis, res => {
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
        uploadlocalstorage(file, certinfo, fthis, res => {
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

export function getUserInfoFun(self) {
    userinfos(data => {
        if (data.code === 1000) {
            self.$store.dispatch("doUserinfo", data.data);
        } else {
            self.$message.error("用户信息获取失败")
        }
    }, {"methods": "GET"})
}

function getChar(n) {
    let SL = [];
    for (let i = 65; i <= n + 65; i++) {
        SL.push(String.fromCharCode(i))
    }
    return SL
}

export function makeFiveC() {
    let SL = [];
    for (const i of getChar(10)) {
        for (const j of getChar(5)) {
            SL.push(i + j)
        }
    }
    return SL
}

export function diskSize(num) {
    if (num === 0) return '0 B';
    let k = 1024; //设定基础容量大小
    let sizeStr = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']; //容量单位
    let i = 0; //单位下标和次幂
    for (let l = 0; l < 8; l++) {   //因为只有8个单位所以循环八次
        if (num / Math.pow(k, l) < 1) { //判断传入数值 除以 基础大小的次幂 是否小于1，这里小于1 就代表已经当前下标的单位已经不合适了所以跳出循环
            break; //小于1跳出循环
        }
        i = l; //不小于1的话这个单位就合适或者还要大于这个单位 接着循环
    }
    return (num / Math.pow(k, i)).toFixed(1) + ' ' + sizeStr[i];  //循环结束 或 条件成立 返回字符
}

export function upspeed(start_time, file_size, percent) {
    const now_time = Date.now();
    return diskSize(file_size * percent * 10 / (now_time - start_time))
}

export function sort_compare(propertyName) {
    return function (object1, object2) {
        let value1 = object1[propertyName];
        let value2 = object2[propertyName];
        if (value2 < value1) {
            return 1;
        } else if (value2 > value1) {
            return -1;
        } else {
            return 0;
        }
    }
}

export function format_choices(key, obj) {
    for (let i = 0; i < obj.length; i++) {
        if (key === obj[i].id) {
            return obj[i].name
        }
    }
    return "未知"
}

//滚动条在Y轴上的滚动距离

export function getScrollTop(){
    let scrollTop = 0, bodyScrollTop = 0, documentScrollTop = 0;
    if(document.body){
        bodyScrollTop = document.body.scrollTop;
    }
    if(document.documentElement){
        documentScrollTop = document.documentElement.scrollTop;
    }
    scrollTop = (bodyScrollTop - documentScrollTop > 0) ? bodyScrollTop : documentScrollTop;
    // return Math.ceil(scrollTop);
    return scrollTop;
}



//文档的总高度
export function getScrollHeight(){
    let scrollHeight = 0, bodyScrollHeight = 0, documentScrollHeight = 0;
    if(document.body){
        bodyScrollHeight = document.body.scrollHeight;
    }
    if(document.documentElement){
        documentScrollHeight = document.documentElement.scrollHeight;
    }
    scrollHeight = (bodyScrollHeight - documentScrollHeight > 0) ? bodyScrollHeight : documentScrollHeight;
    return scrollHeight;
}



//浏览器视口的高度
export function getWindowHeight(){
    let windowHeight = 0;
    if(document.compatMode === "CSS1Compat"){
        windowHeight = document.documentElement.clientHeight;
    }else{
        windowHeight = document.body.clientHeight;
    }
    return windowHeight;
}

export function getappinfo(file,successcallback,errcallback) {
    const AppInfoParser = require('app-info-parser');
    const parser = new AppInfoParser(file);
    let analyseappinfo={};
    parser.parse().then(result => {
         analyseappinfo.icon = result.icon;
         analyseappinfo.filename = file.name;
         analyseappinfo.filesize = file.size;
        if(result.CFBundleDisplayName){
             analyseappinfo.appname = result.CFBundleDisplayName;
             analyseappinfo.bundleid = result.CFBundleIdentifier;
             analyseappinfo.version = result.CFBundleShortVersionString;
             analyseappinfo.buildversion = result.CFBundleVersion;
             analyseappinfo.miniosversion = result.MinimumOSVersion;
            if(result.mobileProvision.ProvisionedDevices){
                 analyseappinfo.release_type='Adhoc';
                 analyseappinfo.release_type_id=1;
                 analyseappinfo.udid=result.mobileProvision.ProvisionedDevices;
            }else {
                 analyseappinfo.release_type='Inhouse';
                 analyseappinfo.release_type_id=2;
                 analyseappinfo.udid=[];
            }
             analyseappinfo.type = 'iOS';
        }else {
             analyseappinfo.appname = result.application.label[0];
             analyseappinfo.bundleid = result.package;
             analyseappinfo.version = result.versionName;
             analyseappinfo.buildversion = result.versionCode;
             analyseappinfo.miniosversion = result.usesSdk.minSdkVersion;
             analyseappinfo.type = 'Android';
             analyseappinfo.release_type = 'Android';
             analyseappinfo.release_type_id=0;

        }
        successcallback(analyseappinfo)

    }).catch(err => {
        errcallback(err);
    });
}

export function uploadqiniuoss(file,certinfo,app,successcallback,processcallback){
    // let app = this;
    // let file=this.currentfile;
    let observer = {
        next(res){
            processcallback(Math.round(res.total.percent));
        },
        error(err){
            // eslint-disable-next-line no-console
            console.log(err);
            app.$message({
                message:file.name + '上传失败，请刷新页面重试',
                type: 'error',
                duration:0
            });
        },
        complete(res){
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
    let config={};
    let observable = app.qiniu.upload(file, certinfo.upload_key, certinfo.upload_token, putExtra, config);
    // eslint-disable-next-line no-unused-vars
    let subscription = observable.subscribe(observer) // 上传开始
    // subscription.unsubscribe() // 上传取消
}

export function dataURLtoFile(dataurl, filename) {//将base64转换为文件
    let arr = dataurl.split(','), mime = arr[0].match(/:(.*?);/)[1],
        bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
    while(n--){
        u8arr[n] = bstr.charCodeAt(n);
    }
    return new File([u8arr], filename, {type:mime});
}
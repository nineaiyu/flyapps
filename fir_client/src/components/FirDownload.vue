<template>
    <el-container>
        <meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=0">
        <el-header>

        </el-header>
        <el-main>
            <div class="wechat_tip_content" v-if="agent === 'wxandroid' || agent === 'wxapple'">
                <div class="wechat_tip" v-show="agent === 'wxandroid'">
                    <i class="triangle-up"></i>请点击右上角<br>选择"在浏览器打开"
                </div>
                <div class="wechat_tip" v-show="agent === 'wxapple'">
                    <i class="triangle-up"></i>请点击右上角<br>选择"在Safari中打开"
                </div>
            </div>
            <div v-else>
                <!--                <span class="pattern left"><img src="../assets/download_pattern_left.png"></span>-->
                <!--                <span class="pattern right"><img src="../assets/download_pattern_right.png"></span>-->
            </div>

            <el-container class="out-container" v-if="wxeasytypeflag">

                <div class="main">
                    <!--                    <div class="main" v-if="(agent !== 'wxandroid' && agent !== 'wxapple')">-->
                    <header>
                        <div class="table-container">
                            <div class="cell-container">
                                <div class="app-brief">
                                    <div class="icon-container wrapper">
                                        <i class="i bg-path"></i>
                                        <span class="icon"><img
                                                :src="mcurrentappinfo.icon_url"></span>
                                        <span id="qrcode" class="qrcode">
                                        </span>
                                    </div>
                                    <p v-if="currentappinfo.issupersign" class="scan-tips wrapper icon-warp">超级签</p>
                                    <p v-else class="scan-tips wrapper icon-warp">{{
                                        mcurrentappinfo.release_type|getiOStype }}</p>
                                    <h1 class="name wrapper">
                                        <span class="icon-warp" style="margin-left:0px">
                                            <i v-if="currentappinfo.type === 0 && agent !== ''"
                                               class="iconfont icon-android2"/>
                                            <i v-if="currentappinfo.type === 1 && agent !== ''"
                                               class="iconfont icon-ios"/>

                                            {{ currentappinfo.name }}
                                        </span>
                                    </h1>

                                    <p class="scan-tips" style="margin-left:170px">扫描二维码下载<br/>或用手机浏览器输入这个网址：<span
                                            class="text-black">{{ full_url }}</span></p>

                                    <div class="release-info">
                                        <p>{{ mcurrentappinfo.app_version }}（Build {{ mcurrentappinfo.build_version }}）-
                                            {{ mcurrentappinfo.binary_size }}</p>
                                        <p>更新于：{{ mcurrentappinfo.created_time |formatTime}}</p>
                                        <p class="version" v-if="mcurrentappinfo.changelog && agent === ''">
                                            更新日志：{{ mcurrentappinfo.changelog }}
                                        </p>
                                    </div>

                                    <div id="actions" class="actions" v-if="agent !==''">

                                        <el-button type="info" round
                                                   v-if="agent === 'wxandroid' || agent === 'wxapple'">不支持在微信内下载
                                        </el-button>

                                        <button type="button" v-else-if="wrong">{{ msg }}</button>
                                        <div v-else>
                                            <div v-if="isdownload">
                                                <div v-if="gomobile">
                                                    <button disabled="" class="loading"
                                                            style="min-width: 42px; width: 42px; padding: 21px 0; border-top-color: transparent; border-left-color: transparent;">
                                                    </button>
                                                </div>
                                                <div v-else>
                                                    <div class="actions type-ios">
                                                        <div><p>正在安装，请按 Home 键在桌面查看</p>
                                                            <p v-if="!this.currentappinfo.issupersign">
                                                                <button @click="gomobileaction">
                                                                    <el-link icon="el-icon-loadings" type="primary"
                                                                             :underline="false">
                                                                        立即信任
                                                                    </el-link>
                                                                </button>

                                                            </p>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>

                                            <div v-else>
                                                <div v-if="currentappinfo.need_password"
                                                     style="margin:0 auto; width:166px">
                                                    <el-input prefix-icon="el-icon-lock" clearable
                                                              placeholder="请输入密码" v-model="password"
                                                              icon="el-icon-loadings" type="primary"
                                                              :underline="false"></el-input>
                                                </div>
                                                <el-divider v-if="currentappinfo.need_password"></el-divider>
                                                <button @click="download">
                                                    <el-link icon="el-icon-loadings" type="primary"
                                                             :underline="false">
                                                        下载安装
                                                    </el-link>
                                                </button>
                                            </div>

                                        </div>

                                    </div>

                                </div>
                            </div>
                        </div>
                    </header>

                    <div class="per-type-info section" v-if="currentappinfo.app_id && agent === ''">
                        <div class="type" v-if="miscomboappinfo.release_id">
                            <div class="info">
                                <p class="type-icon" v-if="iscomboappinfo.type === 0">
                                    <i class="iconfont icon-android2"/>
                                </p>
                                <p class="type-icon" v-else>
                                    <i class="iconfont icon-ios"/>
                                </p>
                                <p class="version">
                                    关联版本：{{ miscomboappinfo.app_version }}（Build {{ miscomboappinfo.build_version }}）
                                </p>
                                <p class="version">
                                    文件大小：{{ miscomboappinfo.binary_size }}<br>
                                </p>
                                <p class="version">
                                    更新于：{{ miscomboappinfo.created_time |formatTime }}
                                </p>
                                <p class="version" v-if="miscomboappinfo.changelog">
                                    更新日志：{{ miscomboappinfo.changelog }}
                                </p>
                            </div>
                        </div>

                        <div class="type">
                            <div class="info">
                                <p class="type-icon" v-if="currentappinfo.type === 0">
                                    <i class="iconfont icon-android2"/>
                                </p>
                                <p class="type-icon" v-else>
                                    <i class="iconfont icon-ios"/>
                                </p>
                                <p class="version">
                                    当前版本：{{ mcurrentappinfo.app_version }}（Build {{ mcurrentappinfo.build_version }}）
                                </p>
                                <p class="version">
                                    文件大小：{{ mcurrentappinfo.binary_size }}
                                </p>
                                <p class="version">
                                    更新于：{{ mcurrentappinfo.created_time|formatTime}}
                                </p>
                                <p class="version" v-if="mcurrentappinfo.changelog">
                                    更新日志：{{ mcurrentappinfo.changelog }}
                                </p>
                            </div>
                        </div>
                    </div>
                    <div class="per-type-info " v-else>
                        <div class="release-info">
                            <div class="info" v-if="mcurrentappinfo.changelog">
                                <h3>更新日志</h3>
                                {{ mcurrentappinfo.changelog }}
                            </div>
                        </div>

                    </div>
                </div>

            </el-container>
            <div v-else>
                <i>
                    {{this.currentappinfo.name | formatName}}
                </i>
            </div>

        </el-main>
    </el-container>


</template>

<script>
    import QRCode from 'qrcodejs2'

    import {getShortAppinfo, getdownloadurl} from '../restful'

    export default {
        name: "FirDownload",
        data() {
            return {
                currentappinfo: {},
                iscomboappinfo: {},
                mcurrentappinfo: {},
                miscomboappinfo: {},
                tmpinfo: {},
                full_url: "",
                agent: '',
                wrong: false,
                msg: '',
                password: '',
                dchoice: false,
                downloadurl: "",
                isdownload: false,
                udid: "",
                wxeasytypeflag: false,
                timer: '',
                gomobile: true,
                mobileprovision: '',
            }
        },
        beforeDestroy() {
            clearTimeout(this.timer);
        },
        methods: {
            gomobileaction() {
                window.location.href = this.mobileprovision;
            },
            download() {
                if (this.currentappinfo.app_id) {
                    this.isdownload = true;
                    getdownloadurl(res => {
                        if (res.code === 1000) {
                            if (res.data.download_url === "") {
                                window.location.href = this.full_url.split("?")[0];
                                // window.location.href = this.full_url;
                                return
                            }
                            if (this.currentappinfo.type === 1) {
                                if (this.currentappinfo.issupersign) {
                                    if (this.$route.query.udid && this.udid === this.$route.query.udid) {
                                        if (this.agent !== '') {
                                            let download_url = res.data.download_url;
                                            this.downloadurl = "itms-services://?action=download-manifest&url=" + encodeURIComponent(download_url);
                                            // eslint-disable-next-line no-unused-vars
                                            this.timmer = setTimeout(data => {
                                                this.gomobile = false;
                                            }, 5000);

                                        }
                                    } else {
                                        if (this.agent !== '') {
                                            this.downloadurl = res.data.download_url;
                                            window.location.href = this.downloadurl;
                                            if (res.data.extra_url !== "") {
                                                // eslint-disable-next-line no-unused-vars
                                                this.timmer = setTimeout(data => {
                                                    window.location.href = res.data.extra_url;
                                                }, 3000);
                                            }

                                            return;
                                        }
                                    }
                                } else {
                                    let download_url = res.data.download_url;
                                    this.downloadurl = "itms-services://?action=download-manifest&url=" + encodeURIComponent(download_url);
                                    if (res.data.extra_url !== "") {
                                        this.mobileprovision = res.data.extra_url;
                                        // eslint-disable-next-line no-unused-vars
                                        this.timmer = setTimeout(data => {
                                            this.gomobile = false;
                                        }, 5000);
                                    }
                                }
                            } else {
                                if (this.agent !== '') {
                                    this.downloadurl = res.data.download_url;
                                }
                            }

                            window.location.href = this.downloadurl;
                        } else {
                            this.isdownload = false;
                            this.password = '';
                            this.$message({
                                message: "密码错误，或者下载链接失效",
                                type: 'error',
                            });
                        }
                    }, {
                        'data': {
                            'token': this.mcurrentappinfo.download_token,
                            'short': this.currentappinfo.short,
                            'release_id': this.mcurrentappinfo.release_id,
                            'password': this.password,
                            'udid': this.udid,
                        },
                        'app_id': this.currentappinfo.app_id
                    })
                }
            },
            qrcode() {
                let qrcode = document.getElementById("qrcode");
                if (qrcode) {
                    new QRCode(qrcode, {
                        width: 100,
                        height: 100,
                        text: location.href, // 二维码地址
                    })
                }

            },
            auto_redircet_url(domain_name) {
                if (domain_name) {
                    let nurl = location.href.split("//")[1].split("/");
                    const user_hostname = domain_name.split("//");
                    if (nurl[0] === user_hostname[1]) {
                        return true;
                    } else {
                        nurl[0] = user_hostname[1];
                        window.location.href = user_hostname[0] + "//" + nurl.join("/");
                        return false;
                    }
                }
            },
            getDownloadTokenFun() {
                let params = {"short": this.$route.params.short, "time": new Date().getTime()};
                if (this.$route.query.release_id) {
                    params["release_id"] = this.$route.query.release_id
                }
                if (this.$route.query.udid) {
                    params["udid"] = this.$route.query.udid
                } else {
                    params["udid"] = ""
                }
                getShortAppinfo(data => {
                    if (data.code === 1000) {
                        if (!this.auto_redircet_url(data.domain_name)) {
                            return;
                        }
                        this.udid = data.udid;
                        if (!data.data.master_release.release_id) {
                            this.$message({
                                message: "该 release 版本不存在,请检查",
                                type: 'error',
                                duration: 0
                            });
                            return
                        }

                        if (this.agent === "android" || this.agent === "wxandroid") {
                            // 请求的数据iOS
                            if (data.data.type === 1) {
                                if (data.data.has_combo) {
                                    if (!params.release_id) {
                                        this.currentappinfo = data.data.has_combo;
                                        this.mcurrentappinfo = data.data.has_combo.master_release;
                                    } else {
                                        this.wrong = true;
                                        this.msg = '该 release 版本只能在苹果设备使用';
                                    }
                                    this.iscomboappinfo = data.data;
                                    this.miscomboappinfo = data.data.master_release;

                                } else {
                                    this.wrong = true;
                                    this.msg = '苹果应用不支持安卓设备';
                                    this.dchoice = true;

                                }
                            } else {
                                this.dchoice = true;
                            }
                        } else if (this.agent === "apple" || this.agent === "wxapple") {
                            if (data.data.type === 0) {
                                if (data.data.has_combo) {
                                    if (!params.release_id) {
                                        this.currentappinfo = data.data.has_combo;
                                        this.mcurrentappinfo = data.data.has_combo.master_release;
                                    } else {
                                        this.wrong = true;
                                        this.msg = '该 release 版本只能在安卓设备使用';
                                    }
                                    this.iscomboappinfo = data.data;
                                    this.miscomboappinfo = data.data.master_release;

                                } else {
                                    this.wrong = true;
                                    this.msg = '安卓应用不支持苹果设备';
                                    this.dchoice = true;

                                }
                            } else {
                                this.dchoice = true;
                            }
                        } else {
                            this.dchoice = true;
                        }

                        if (this.dchoice) {
                            this.currentappinfo = data.data;
                            this.mcurrentappinfo = data.data.master_release;
                            if (this.currentappinfo.has_combo) {
                                this.iscomboappinfo = this.currentappinfo.has_combo;
                                this.miscomboappinfo = this.currentappinfo.has_combo.master_release;
                            }
                        }

                        if (this.agent !== '') {
                            this.miscomboappinfo = {};
                            this.iscomboappinfo = {};
                        }
                        if (this.currentappinfo.wxeasytype) {
                            if (this.agent !== 'wxandroid' && this.agent !== 'wxapple') {
                                document.title = this.currentappinfo.name + '下载';
                                this.wxeasytypeflag = true;
                            } else {
                                document.title = '请在浏览器中打开';
                            }
                        } else {
                            document.title = this.currentappinfo.name + '下载';
                            this.wxeasytypeflag = true;

                        }

                        if (this.currentappinfo.wxredirect) {
                            if (this.mcurrentappinfo.binary_url && this.agent !== '' && this.wrong === false) {
                                window.location.href = this.mcurrentappinfo.binary_url
                            }
                        }
                    } else {
                        this.$message({
                            message: data.msg,
                            type: 'error',
                            duration: 0
                        });
                    }
                }, params)
            },
            getAgent() {
                const ua = navigator.userAgent.toLowerCase();

                const browser = {
                    versions: function () {
                        const u = navigator.userAgent;
                        return {//移动终端浏览器版本信息
                            trident: u.indexOf('Trident') > -1, //IE内核
                            presto: u.indexOf('Presto') > -1, //opera内核
                            webKit: u.indexOf('AppleWebKit') > -1, //苹果、谷歌内核
                            gecko: u.indexOf('Gecko') > -1 && u.indexOf('KHTML') == -1, //火狐内核
                            mobile: !!u.match(/AppleWebKit.*Mobile/i) || !!u.match(/MIDP|SymbianOS|NOKIA|SAMSUNG|LG|NEC|TCL|Alcatel|BIRD|DBTEL|Dopod|PHILIPS|HAIER|LENOVO|MOT-|Nokia|SonyEricsson|SIE-|Amoi|ZTE/), //是否为移动终端
                            ios: !!u.match(/\(i[^;]+;( U;)? CPU.+Mac OS X/), //ios终端
                            android: u.indexOf('Android') > -1 || u.indexOf('Linux') > -1, //android终端或者uc浏览器
                            iPhone: u.indexOf('iPhone') > -1 || u.indexOf('Mac') > -1, //是否为iPhone或者QQHD浏览器
                            iPad: u.indexOf('iPad') > -1, //是否iPad
                            webApp: u.indexOf('Safari') === -1, //是否web应该程序，没有头部与底部
                            macos: u.indexOf('Mac OS') > -1 && u.indexOf('Macintosh') > -1
                        };
                    }(),
                    language: (navigator.browserLanguage || navigator.language).toLowerCase()
                };
                if (browser.versions.iPhone || browser.versions.iPad || browser.versions.ios) {//苹果版

                    if (ua.match(/micromessenger/i) && ua.match(/micromessenger/i)[0] === "micromessenger") {
                        this.agent = 'wxapple';
                        //微信
                    } else {
                        if(browser.versions.macos){
                            this.agent='';
                        }else {
                            this.agent = 'apple';
                        }
                    }

                }
                if (browser.versions.android) {//安卓
                    if (ua.match(/micromessenger/i) && ua.match(/micromessenger/i)[0] === "micromessenger") {
                        // alert('安卓微信');
                        this.agent = 'wxandroid';
                        //微信
                    } else {
                        //  正常浏览器
                        this.agent = 'android';

                    }
                }
                if (this.agent === '') {
                    this.wxeasytypeflag = true;
                }

            }
        }, created() {
            this.getAgent();
        }, mounted() {
            this.getDownloadTokenFun();
            // this.full_url = location.href.split("?")[0];
            this.full_url = location.href;
            this.qrcode();
        }, filters: {
            getiOStype: function (type) {
                let ftype = '';
                if (type === 1) {
                    ftype = '内测版'
                } else if (type === 2) {
                    ftype = '企业版'
                }
                return ftype
            },
            formatName: function (name) {
                if (name) {
                    return name.replace("麻将", "").replace("斗地主", "").replace("棋牌", "")
                }
            },
            formatTime: function (stime) {
                if (stime) {
                    stime = stime.split(".")[0].split("T");
                    return stime[0] + " " + stime[1]
                }
            }
        }
    };


</script>

<style scoped>

    .text-black {
        color: #505556
    }

    .wechat_tip, .wechat_tip > i {
        position: absolute;
        right: 10px
    }

    .wechat_tip {
        display: -webkit-box;
        display: -ms-flexbox;
        display: flex;
        -webkit-box-align: center;
        -ms-flex-align: center;
        align-items: center;
        -webkit-box-pack: center;
        -ms-flex-pack: center;
        justify-content: center;
        background: #3ab2a7;
        color: #fff;
        font-size: 14px;
        font-weight: 500;
        width: 135px;
        height: 60px;
        border-radius: 10px;
        top: 15px
    }

    .wechat_tip > i {
        top: -10px;
        width: 0;
        height: 0;
        border-left: 6px solid transparent;
        border-right: 6px solid transparent;
        border-bottom: 12px solid #3ab2a7
    }

    .mask img {
        max-width: 100%;
        height: auto
    }


    /*上面是微信的*/

    a, button {
        cursor: pointer
    }

    .out-container, .pattern {
        -webkit-transition: all .5s
    }

    .main, .out-container {
        display: block;
        height: 100%
    }

    *, .wechat-tips {
        box-sizing: border-box
    }

    .desc-section pre, .releases-section .release-view .version-info .changelog .wrapper, body, html {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif
    }


    .el-container {
        margin: 0;
        padding: 0;
        height: 100%;
        color: #a9b1b3;
        font-size: 14px;
        /*background-color: #fff;*/
        -webkit-font-smoothing: antialiased
    }

    .no-scroll {
        overflow: hidden
    }

    .text-center {
        text-align: center
    }

    .text-black {
        color: #505556
    }

    p {
        margin-top: 0
    }

    a {
        text-decoration: none
    }

    button {
        padding: 0;
        border: 1px solid #a9b1b3;
        background-color: transparent
    }

    button:focus {
        outline: 0
    }

    .pattern {
        position: absolute;
        top: 0;
        z-index: 1;
        max-width: 312px;
        width: 21.66%;
        transition: all .5s
    }

    .pattern.left {
        left: 0
    }

    .pattern.right {
        right: 0
    }

    .pattern img {
        width: 100%;
        -webkit-transition: all 1s;
        transition: all 1s;
        pointer-events: none
    }

    @media (max-width: 1280px) {
        .pattern {
            width: 18%
        }
    }

    .combo .pattern {
        max-width: 220px
    }

    @media (min-width: 1280px) {
        .combo .pattern {
            max-width: 312px;
            width: 21%
        }
    }

    .out-container {
        position: relative;
        z-index: 2;
        transition: all .5s
    }

    .main {
        margin: 0 auto;
        max-width: 94%;
        width: 700px
    }

    .main .table-container {
        display: table;
        width: 100%;
        height: 100%
    }

    .main .cell-container {
        display: table-cell;
        height: 100%;
        vertical-align: middle;
        text-align: center
    }

    .show-wechat-notice .out-container, .show-wechat-notice .pattern {
        top: 180px
    }

    .show-wechat-notice .notice-wechat {
        height: 180px
    }

    .notice-wechat {
        position: absolute;
        top: 0;
        left: 0;
        z-index: 1;
        width: 100%;
        height: 0;
        background-color: #505556;
        box-shadow: 0 -9px 29px -7px rgba(0, 0, 0, .1) inset;
        -webkit-transition: all .5s;
        transition: all .5s
    }

    .constraint .main header, .expired .main header, .forbidden .main header, .legal_forbidden .main header, .not_found .main header {
        opacity: 1;
        -webkit-transition: all .5s;
        transition: all .5s;
        -webkit-transform: none;
        transform: none
    }

    .constraint .main header h1, .expired .main header h1, .forbidden .main header h1, .legal_forbidden .main header h1, .not_found .main header h1 {
        color: #505556;
        font-weight: 400;
        font-size: 28px
    }

    .constraint .main header h3, .expired .main header h3, .forbidden .main header h3, .legal_forbidden .main header h3, .not_found .main header h3 {
        font-size: 18px;
        cursor: default
    }

    .constraint .main header h3 label, .expired .main header h3 label, .forbidden .main header h3 label, .legal_forbidden .main header h3 label, .not_found .main header h3 label {
        cursor: default
    }

    .constraint .main header p, .expired .main header p, .forbidden .main header p, .legal_forbidden .main header p, .not_found .main header p {
        font-size: 16px;
        line-height: 24px
    }

    .constraint .main .fade-out, .expired .main .fade-out, .forbidden .main .fade-out, .legal_forbidden .main .fade-out, .not_found .main .fade-out {
        opacity: 0;
        -webkit-transform: translateY(-40px);
        transform: translateY(-40px)
    }

    .constraint .pattern img, .expired .pattern img, .forbidden .pattern img, .legal_forbidden .pattern img, .not_found .pattern img {
        -webkit-filter: grayscale(1)
    }

    @media screen and (max-width: 480px) {
        .constraint .cell-container, .forbidden .cell-container, .legal_forbidden .cell-container, .not_found .cell-container {
            vertical-align: top
        }
    }


    @media screen and (max-width: 425px) {
        .error-container pre, .error-container small {
            display: none
        }

        .error-container {
            width: 100%;
            margin-top: 100px;
            margin-bottom: 50px;
            text-align: center
        }

        .error-container h1 {
            padding: 0 70px
        }
    }

    .back-btn {
        position: fixed;
        top: 28px;
        left: 28px;
        z-index: 3;
        width: 60px;
        height: 60px;
        border: 1px solid #bdc6c7;
        border-radius: 60px;
        background-color: #fff
    }

    .back-btn i {
        display: block;
        margin-top: 29px;
        margin-left: 21px
    }

    .back-btn i:after, .back-btn i:before {
        position: absolute;
        display: inline-block;
        width: 16px;
        height: 1px;
        background-color: #505556;
        content: ' ';
        -webkit-transform-origin: left;
        transform-origin: left
    }

    .back-btn i:before {
        -webkit-transform: rotateZ(-42deg);
        transform: rotateZ(-42deg)
    }

    .back-btn i:after {
        -webkit-transform: rotateZ(42deg);
        transform: rotateZ(42deg)
    }


    .combo .main {
        min-width: 960px;
        max-width: 100%
    }

    .data_error .icon, .error .icon, .forbidden .icon, .passwd .icon {
        margin-bottom: 40px;
        width: 120px;
        height: 120px;
        border-radius: 22.7px
    }

    @media screen and (min-height: 520px) {
        .data_error form, .error form, .forbidden form, .passwd form {
            margin-bottom: 100px
        }
    }

    .data_error .main, .error .main, .forbidden .main, .passwd .main {
        height: 100%
    }

    .data_error .main table, .error .main table, .forbidden .main table, .passwd .main table {
        width: 100%;
        height: 100%;
        vertical-align: middle
    }

    .data_error .app-brief h1, .error .app-brief h1, .forbidden .app-brief h1, .passwd .app-brief h1 {
        text-transform: uppercase
    }

    .data_error .reload, .error .reload, .forbidden .reload, .passwd .reload {
        color: #a9b1b3;
        font-size: 12px;
        text-decoration: none;
        border: 1px solid #a9b1b3;
        background-color: transparent;
        padding: 6px 12px;
        border-radius: 40px
    }

    .data_error .no-release-tips, .error .no-release-tips, .forbidden .no-release-tips, .passwd .no-release-tips {
        line-height: 20px;
        max-width: 80%;
        margin: 0 auto
    }

    .data_error .no-release-tips a, .error .no-release-tips a, .forbidden .no-release-tips a, .passwd .no-release-tips a {
        text-decoration: underline;
        color: #9b9b9b
    }

    #passwd-wrong {
        display: none
    }

    .passwd form {
        text-align: center
    }

    .passwd form h4 {
        font-weight: 400;
        font-size: 18px
    }

    .passwd form button, .passwd form input {
        padding: 12px 20px;
        width: 300px;
        border: 1px solid #f8ba0b;
        border-radius: 5px;
        font-size: 16px
    }

    .passwd form button:focus, .passwd form input:focus {
        outline: 0
    }

    .passwd form input {
        color: #f8ba0b;
        text-align: center
    }

    .passwd form button {
        border-color: #f8ba0b;
        background-color: #f8ba0b;
        color: #fff;
        cursor: pointer
    }

    .main .icon-container {
        position: relative;
        margin: 0 auto;
        width: 290px;
        height: 290px
    }

    .main .icon-container .bg-path {
        position: absolute;
        top: 4px;
        left: 4px;
        z-index: 1;
        color: #eff2f2;
        font-size: 290px
    }

    .main .icon-container span {
        position: absolute;
        z-index: 2;
        display: block
    }

    .main .icon-container .icon {
        top: 0;
        left: 0;
        padding: 10px;
        width: 140px;
        height: 140px;
        border-radius: 17.54%;
        background-color: #fff
    }

    .main .icon-container .icon img {
        max-width: 100%;
        width: 120px;
        height: 120px;
        border-radius: 17.54%
    }

    .main .icon-container .qrcode {
        right: 0;
        bottom: 0;
        width: 140px;
        height: 140px;
        border: 20px solid transparent;
        border-radius: 26px
    }

    .main .icon-container .qrcode img {
        width: 100px;
        height: 100px
    }

    .main > header {
        display: block;
        min-height: 600px;
        max-height: 800px;
        height: 100%
    }

    .main > header.ad-app {
        height: auto
    }

    .main > header .wrapper {
        margin-right: auto;
        margin-left: auto;
        width: 290px
    }

    .main > header .app-brief {
        -webkit-transition: all .5s;
        transition: all .5s
    }

    .main > header .name, .main > header body.passwd .name {
        position: relative;
        margin: 20px auto;
        width: 290px;
        color: #505556;
        text-align: left;
        font-weight: 400;
        font-size: 28px
    }

    .main > header .name i, .main > header body.passwd .name i {
        position: absolute;
        right: 100%;
        top: 10px;
        margin-right: 10px;
        font-size: 26px
    }

    .main > header .name span, .main > header body.passwd .name span {
        display: inline-block;
        max-width: 100%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        word-wrap: normal;
        line-height: 1.6
    }

    .main > header .release-type {
        margin: 24px auto 0;
        width: 290px;
        text-align: left
    }

    .main > header .scan-tips {
        margin: 0 auto;
        width: 290px;
        text-align: left;
        white-space: nowrap;
        line-height: 22px
    }

    .main > header .release-info {
        position: relative;
        margin-top: 30px;
        margin-bottom: 30px;
        padding-top: 30px
    }

    .main > header .release-info p {
        margin-bottom: 4px
    }

    .main > header .release-info:before {
        position: absolute;
        top: 0;
        left: 50%;
        display: block;
        margin-left: -30%;
        width: 60%;
        border-top: 1px solid #dae2e3;
        content: ' '
    }

    .main > header .actions {
        margin: 30px auto 0;
        max-width: 290px
    }

    .main > header .actions p {
        line-height: 1.5;
        padding: 12px;
        color: #3AB2A7;
        font-weight: 500;
        font-size: 16px
    }

    .main > header .actions button {
        display: inline-block;
        padding: 12px 46px;
        min-width: 200px;
        border: 1px solid #32b2a7;
        border-radius: 40px;
        font-size: 14px;
        background: #32b2a7;
        color: #fff
    }

    .main > header .actions button a {
        color: #fff
    }

    .main > header .actions a {
        color: #868c8e;
        font-size: 14px;
        display: block
    }

    .main > header .type-ios {
        display: none
    }

    @media only screen and (max-width: 768px) {
        .main > header {
            max-height: 100%;
            height: 100%;
            min-height: 400px
        }

        .main > header.ad-app {
            min-height: 700px
        }

        .main > header .type-ios {
            display: block
        }
    }

    .master-section {
        overflow: hidden;
        padding: 40px 0
    }

    @media screen and (max-width: 768px) {
        .main > header {
            min-height: 400px
        }

        .main > header .release-type {
            display: none
        }

        .main > header .release-info {
            display: block
        }

        .main > header .name {
            text-align: center;
            font-size: 24px
        }

        .main > header .name .icon-warp {
            position: static;
            display: inline-block;
            margin-left: -48px;
            max-width: 76%
        }

        .main > header .name .tip {
            margin-top: 5px
        }

        .main > header .name i {
            position: static
        }

        .main > header .scan-tips {
            display: none
        }

        .master-section {
            text-align: center
        }

        .master-section .store-link {
            display: inline-block;
            float: none;
            margin-bottom: 0
        }

        .master-section p {
            display: none
        }
    }

    .master-section p {
        margin: 0;
        line-height: 21px
    }

    .master-section pre {
        text-align: left;
        white-space: pre-line;
        word-wrap: break-word;
        word-break: break-all;
        line-height: 22px
    }

    .footer, .per-type-info .info, .releases-section .release-view .qrcode, .section-store-link, .store-section {
        text-align: center
    }


    .section {
        position: relative;
        z-index: 2;
        padding: 50px 0;
        border-top: 1px solid #dae2e3
    }

    @media screen and (max-width: 768px) {
        .section {
            padding: 50px 20px
        }
    }

    .section h2 {
        margin: 0 0 40px;
        color: #505556;
        font-weight: 400
    }

    .store-section .store-link {
        display: block;
        margin: 0 auto;
        padding: 14px 40px 10px;
        width: 260px;
        border: 1px solid #505556;
        border-radius: 5px;
        background-color: transparent;
        color: #505556;
        font-size: 28px
    }

    .per-type-info {
        position: relative;
        overflow: hidden;
        padding-top: 0;
        border-top: 1px solid #dae2e3
    }

    .per-type-info .type {
        float: left;
        width: 50%
    }

    .per-type-info .type:first-child .releases-section {
        padding: 70px 70px 0 0
    }

    .per-type-info .type .master-section {
        padding: 70px 0 0;
        border-top: 0
    }

    .per-type-info .type .master-section pre {
        white-space: pre-line
    }

    .per-type-info .type:last-child .master-section, .per-type-info .type:last-child .releases-section {
        padding: 70px 0 0 70px
    }

    .per-type-info .type-icon {
        margin-bottom: 0
    }

    .per-type-info .info {
        padding-top: 50px;
        font-size: 12px
    }

    .per-type-info .info .version {
        margin-bottom: 20px
    }

    .per-type-info .info .type-icon {
        margin-bottom: 40px
    }

    .per-type-info .info i {
        margin-bottom: 0;
        color: #505556;
        font-size: 48px
    }

    .per-type-info .info .store-link-wrapper a {
        width: 200px
    }

    .per-type-info .info .store-link-wrapper a i {
        font-size: 29px
    }

    .per-type-info:before {
        position: absolute;
        left: 50%;
        width: 1px;
        height: 100%;
        background-color: #dae2e3;
        content: ' '
    }

    .desc-section pre {
        white-space: pre-wrap;
        line-height: 22px
    }

    .section-store-link a {
        display: inline-block;
        border: 1px solid #505556;
        border-radius: 5px;
        text-decoration: none
    }

    .section-store-link a i {
        display: block;
        padding: 14px 40px;
        color: #505556;
        font-size: 33px
    }

    .screenshots-section {
        border-bottom: 0
    }

    .screenshots-section .list-wrapper {
        overflow-x: scroll;
        max-width: 100%
    }

    .screenshots-section ul {
        display: block;
        margin: 0;
        padding: 0;
        list-style: none;
        white-space: nowrap
    }

    .screenshots-section ul li {
        display: inline-block;
        padding-right: 20px;
        vertical-align: middle
    }

    .screenshots-section ul li img {
        max-height: 462px
    }

    .type:first-child .master-section {
        padding-right: 5px
    }

    .type:last-child .master-section {
        padding-left: 5px
    }


    .hide {
        display: none
    }

    .wechat-tips img, .wechat-tips span {
        display: inline-block;
        margin-right: 10px;
        vertical-align: middle
    }

    .wechat-tips {
        position: fixed;
        top: 10px;
        z-index: 103;
        padding-top: 14px;
        width: 100%;
        text-align: right
    }

    .wechat-tips span {
        color: #fff;
        text-align: left;
        font-weight: 700;
        font-size: 16px;
        line-height: 30px
    }

    .wechat-tips span.en {
        width: 240px
    }

    .wechat-tips img {
        margin-bottom: 13px;
        width: 50px
    }

    @media (min-width: 420px) {
        .wechat-tips span {
            margin-right: 15px
        }

        .wechat-tips span.en {
            margin-bottom: -20px;
            width: auto
        }

        .wechat-tips img {
            margin-right: 20px
        }
    }

    .list-unstyled {
        margin: 0;
        padding: 0;
        list-style-type: none
    }

    .list-unstyled li:first-child {
        padding-bottom: 10px
    }

    .tip {
        margin-left: 15px;
        vertical-align: middle;
        font-size: 14px;
        cursor: pointer
    }

    .tip.en {
        margin-left: 5px
    }

    .tip img {
        margin-right: 5px;
        height: 16px;
        position: relative;
        top: 4px
    }

    .tip.RISK {
        color: #d95656
    }

    .tip.SCANED {
        color: #8fbf46
    }

    .tip.SCANED img {
        height: 14px;
        top: 2px
    }


    @-webkit-keyframes rotate {
        0% {
            -webkit-transform: rotate(0);
            transform: rotate(0)
        }
        100% {
            -webkit-transform: rotate(360deg);
            transform: rotate(360deg)
        }
    }

    @keyframes rotate {
        0% {
            -webkit-transform: rotate(0);
            transform: rotate(0)
        }
        100% {
            -webkit-transform: rotate(360deg);
            transform: rotate(360deg)
        }
    }

    #actions {
        display: none
    }

    #actions button {
        -webkit-transition: all .25s;
        transition: all .25s
    }

    #actions button.loading {
        -webkit-animation: rotate .6s linear infinite;
        animation: rotate .6s linear infinite;
        background: 0
    }

    @media only screen and (min-device-width: 320px) and (max-device-width: 480px) and (-webkit-min-device-pixel-ratio: 2) {
        #actions {
            display: block
        }
    }

    @media only screen and (min-device-width: 320px) and (max-device-width: 568px) and (-webkit-min-device-pixel-ratio: 2) {
        #actions {
            display: block
        }
    }

    @media only screen and (min-device-width: 375px) and (max-device-width: 667px) and (-webkit-min-device-pixel-ratio: 2) {
        #actions {
            display: block
        }
    }

    @media only screen and (min-device-width: 414px) and (max-device-width: 736px) and (-webkit-min-device-pixel-ratio: 3) {
        #actions {
            display: block
        }
    }

    @media only screen and (min-device-width: 768px) and (max-device-width: 1024px) and (-webkit-min-device-pixel-ratio: 1) {
        #actions {
            display: block
        }
    }

    @media only screen and (min-device-width: 768px) and (max-device-width: 1024px) and (-webkit-min-device-pixel-ratio: 2) {
        #actions {
            display: block
        }
    }

    #actions.type-android {
        display: block
    }

    body.hidden-overflow {
        overflow: hidden
    }

    .main header .app-brief .icon-container .qrcode {
        background-color: #eff2f2;
        -webkit-transition: all .25s;
        transition: all .25s
    }

    .main header .app-brief .name .icon-warp {
        vertical-align: bottom
    }

    .main header .app-brief .name > .tip {
        vertical-align: bottom;
        position: relative;
        top: -3px
    }


    .main.forbidden .footer .one-key-report, .main.not_found .footer .one-key-report {
        display: none
    }


    .app_bottom_fixed img {
        width: 100%;
        max-height: 80px
    }


    @media only screen and (max-width: 991px) and (min-width: 768px) {
        .after-install-games-fixed .popularize-games .popularize-list > li:nth-child(n+5) {
            display: none
        }

        .after-install-games-fixed .popularize-games .popularize-list .popularize-app-game {
            margin-bottom: 30px !important
        }
    }

    @media only screen and (max-width: 1024px) and (min-width: 991px) {
        .after-install-games-fixed .popularize-games .popularize-list > li:nth-child(n+6) {
            display: none
        }

        .after-install-games-fixed .popularize-games .popularize-list .popularize-app-game {
            margin-bottom: 30px !important
        }
    }

    .after-install-games-fixed .popularize-games .popularize-list {
        display: -webkit-box;
        display: -ms-flexbox;
        display: flex;
        -ms-flex-wrap: wrap;
        flex-wrap: wrap;
        -ms-flex-pack: distribute;
        justify-content: space-around
    }

    .after-install-games-fixed .popularize-games .popularize-list .popularize-app-game {
        max-width: 180px;
        width: 45%;
        box-shadow: 0 6px 20px 0 rgba(0, 0, 0, .1);
        margin-bottom: 10px;
        border-radius: 20px;
        background: #35a89b
    }

    .after-install-games-fixed .popularize-games .popularize-list .popularize-app-game .app-download {
        font-size: 16px;
        height: 30px;
        display: -webkit-box;
        display: -ms-flexbox;
        display: flex;
        -webkit-box-align: center;
        -ms-flex-align: center;
        align-items: center;
        -webkit-box-pack: center;
        -ms-flex-pack: center;
        justify-content: center;
        color: #fff
    }

    .after-install-games-fixed .popularize-games .popularize-list .popularize-app-game .popularize-app-game-content {
        height: 145px;
        background: #fff;
        display: -webkit-box;
        display: -ms-flexbox;
        display: flex;
        -webkit-box-orient: vertical;
        -webkit-box-direction: normal;
        -ms-flex-direction: column;
        flex-direction: column;
        -webkit-box-align: center;
        -ms-flex-align: center;
        align-items: center;
        border-radius: 20px
    }

    .after-install-games-fixed .popularize-games .popularize-list .popularize-app-game .popularize-app-game-content .app-zhibo-icon-img {
        margin-top: 10px
    }

    .after-install-games-fixed .popularize-games .popularize-list .popularize-app-game .popularize-app-game-content .app-zhibo-icon-img > img {
        border-radius: 5px;
        height: 50px;
        width: 50px
    }

    .after-install-games-fixed .popularize-games .popularize-list .popularize-app-game .primary-text {
        max-width: 80%;
        color: #4a4a4a;
        text-align: center;
        font-size: 16px;
        font-weight: 700
    }

    .after-install-games-fixed .popularize-games .popularize-list .popularize-app-game .secondary-text {
        max-width: 80%;
        height: 32px;
        overflow: hidden;
        text-align: center;
        font-size: 12px;
        color: rgba(93, 103, 109, .9);
        padding-bottom: 5px
    }


    @media screen and (max-height: 500px) {
        .bottom-popularize {
            position: static
        }
    }

    .visiable-moblie {
        display: none
    }

    @media screen and (max-width: 720px) {
        .main .ad-section {
            width: 100%
        }
    }

    @media screen and (max-width: 768px) {
        .combo .main, .main {
            width: 100%;
            min-width: 100%
        }

        .data_error form, .error form, .forbidden form, .passwd form {
            margin-bottom: 30px
        }

        .main .app-brief {
            text-align: center
        }

        .main .app-brief button {
            display: inline-block
        }

        .main .app-brief .bg-path, .main .app-brief .qrcode {
            display: none
        }

        .main .icon-container {
            width: 100%;
            height: auto;
            text-align: center
        }

        .main .icon-container .icon {
            position: static;
            display: inline-block
        }


    }

    @media screen and (min-width: 1024px) {
        .main header .app-brief .icon-container:hover .qrcode {
            -webkit-transform: scale(1.6);
            transform: scale(1.6);
            box-shadow: 0 1px 5px rgba(0, 0, 0, .3)
        }
    }

</style>

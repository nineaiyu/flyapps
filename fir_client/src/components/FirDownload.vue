<template>
    <el-container class="container">
        <meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=0">


        <div class="wechat_tip_content" v-if="(agent === 'wxandroid' || agent === 'wxapple') && !wrong">
            <div class="mask">
                <div class="wechat_tip" v-show="agent === 'wxandroid'">
                    <i class="triangle-up"/>请点击右上角<br>选择"在浏览器打开"
                </div>
                <div class="wechat_tip" v-show="agent === 'wxapple'">
                    <i class="triangle-up"/>请点击右上角<br>选择"在Safari中打开"
                </div>
            </div>
        </div>

        <div v-else>
            <!--            <span class="pattern left"><img src="@/assets/down_left.png"></span>-->
            <!--            <span class="pattern right"><img src="@/assets/down_right.png"></span>-->
        </div>

        <el-container class="out-container " v-if="wxeasytypeflag">

            <div class="main">
                <header>
                    <div class="table-container">
                        <div class="cell-container">
                            <div class="app-brief">
                                <div class="icon-container wrapper">
                                    <i class="i bg-path"/>
                                    <span class="icon"><img
                                            :src="mcurrentappinfo.icon_url" alt=""></span>
                                    <span id="qrcode" class="qrcode">
                                    </span>
                                </div>
                                <p v-if="currentappinfo.issupersign" class="scan-tips wrapper icon-warp">超级签 </p>
                                <p v-else class="scan-tips wrapper icon-warp">{{ mcurrentappinfo.release_type|getiOStype
                                    }}</p>
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

                                <div class="release-info" v-if="currentappinfo.description && agent === ''">
                                    <p class="version">
                                        应用描述：{{ currentappinfo.description }}
                                    </p>
                                </div>
                                <div class="release-info">
                                    <p>{{ mcurrentappinfo.app_version }}（Build {{ mcurrentappinfo.build_version }}）-
                                        {{ mcurrentappinfo.binary_size }}</p>
                                    <p>更新于：{{ mcurrentappinfo.created_time |formatTime}}</p>
                                    <p class="version" v-if="mcurrentappinfo.changelog && agent === ''">
                                        更新日志：{{ mcurrentappinfo.changelog }}
                                    </p>
                                </div>

                                <div id="actions" class="actions" v-if="agent !==''"
                                     style="margin-top: 10%;margin-bottom: 20%">
                                    <button type="button" v-if="wrong">{{ msg }}</button>

                                    <el-button type="info" round
                                               v-else-if="agent === 'wxandroid' || agent === 'wxapple'">
                                        不支持在微信内下载
                                    </el-button>

                                    <div v-else style="margin-top: 10%;margin-bottom: 20%">
                                        <div v-if="isdownload">
                                            <div v-if="gomobile">
                                                <button disabled="" class="loading"
                                                        style="min-width: 42px; width: 42px; padding: 21px 0; border-top-color: transparent; border-left-color: transparent;">
                                                </button>
                                            </div>
                                            <div v-else>
                                                <div class="actions type-ios">
                                                    <div><p>正在安装，请按 Home 键在桌面查看</p>
                                                        <p v-if="!this.currentappinfo.issupersign && this.mcurrentappinfo.release_type!==1">
                                                            <button @click="gomobileaction">
                                                                <el-link icon="el-icon-loadings" type="primary"
                                                                         :underline="false">
                                                                    安装完成后,需立即信任
                                                                </el-link>
                                                            </button>

                                                        </p>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        <div v-else>
                                            <div v-if="currentappinfo.need_password" style="margin:0 auto; width:166px">
                                                <el-input prefix-icon="el-icon-lock" clearable
                                                          placeholder="请输入密码" v-model="password"
                                                          icon="el-icon-loadings" type="primary"
                                                          :underline="false"/>
                                            </div>
                                            <el-divider v-if="currentappinfo.need_password"/>
                                            <button @click="download">
                                                <el-link icon="el-icon-loadings" type="primary"
                                                         :underline="false">
                                                    下载安装
                                                </el-link>
                                            </button>
                                            <a v-if="(currentappinfo.issupersign || mcurrentappinfo.release_type === 2) && !$route.query.udid"
                                               @click="jiaocheng('open')"
                                               class="jiaocheng" style="color: white;font-size: 18px;">?</a>
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
                        <div class="info" v-if="currentappinfo.description">
                            <h3>应用描述</h3>
                            {{ currentappinfo.description }}
                        </div>
                    </div>

                </div>


                <div class="screenshots-section" v-if="imagelist && imagelist.length > 0" style="margin-top: 30%">
                    <el-divider/>
                    <div v-if="miscomboappinfo.release_id">
                        <h3 v-if="currentappinfo.type === 0">
                            Android 应用截图
                        </h3>
                        <h3 v-else>iOS 应用截图</h3>
                    </div>
                    <div v-else>
                        <h3>应用截图</h3>
                    </div>

                    <div class="list-wrapper">
                        <ul>
                            <li v-for="screen in imagelist" :key="screen">
                                <img v-lazy="screen" alt=""/>
                            </li>
                        </ul>
                    </div>

                </div>
                <div class="footer"
                     v-if="(currentappinfo.issupersign || mcurrentappinfo.release_type === 2) && $route.query.udid"
                     style="margin-top: 5%">
                    <el-tag type="success">UDID:</el-tag>
                    <el-tag>
                        {{ $route.query.udid }}
                    </el-tag>
                    <br>
                    <el-link type="warning" :underline="false">若安装异常，请复制UDID，发送给管理员</el-link>
                </div>

                <div class="footer" style="margin-top: 30%;margin-bottom: 8px">
                    免责声明：<br>
                    本网站仅提供下载托管，应用为用户自行上传，请甄别应用风险后进行下载！
                </div>
                <div v-if="agent!==''">
                    <div v-if="ad_info.ad_uri" style="margin-bottom: 80px"/>
                    <div class="app_bottom_fixed" v-if="ad_info.ad_uri">
                        <a :href="ad_info.ad_uri" target="_blank">
                            <img :src="ad_info.ad_pic" alt="welcome" style="object-fit: cover">
                        </a>
                    </div>
                </div>

            </div>

        </el-container>

        <div v-else>
            <i>
                {{this.currentappinfo.name | formatName}}
            </i>
        </div>


        <div ref="signhelp" class="signhelp screenshots-section">
            <div class="signhelp-title">
                iOS安装教程
                <span><a id="closeBtn" @click="jiaocheng('close')">关闭</a></span>
            </div>

            <div class="list-wrapper" style="width: 300px;">
                <ul>
                    <li v-for="sign in signhelplist" :key="sign.url">
                        <img v-lazy="sign.url" :key="sign.url" alt=""/>
                        <p>
                            安装引导<br>{{ sign.msg}}
                        </p>
                    </li>
                </ul>
            </div>


        </div>
        <div ref="bg" class="bg"></div>

    </el-container>


</template>

<script>
    import QRCode from 'qrcodejs2'

    import {getdownloadurl, getShortAppinfo, gettask} from '@/restful'

    export default {
        name: "FirDownload",
        data() {
            return {
                signhelplist: [
                    {msg: '第一步 允许打开配置描述文件', url: require('@/assets/sign/step1.jpg')},
                    {msg: '第二步 点击右上角安装按钮', url: require('@/assets/sign/step2.jpg')},
                    {msg: '第三步 输入开机解锁密码', url: require('@/assets/sign/step3.jpg')},
                    {msg: '第四步 点击下方安装按钮', url: require('@/assets/sign/step4.jpg')},
                ],
                inhousehelplist: [
                    {
                        msg: '首次安装企业版应用时会出现"未受信任的企业级开发者" 提示',
                        url: require('@/assets/inhouse/b1.png')
                    },
                    {msg: '第一步 在手机中打开设置功能，选择 "通用" 功能', url: require('@/assets/inhouse/b2.png')},
                    {msg: '第二步 在通用中，选择 "描述文件与设备管理" 功能', url: require('@/assets/inhouse/b3.png')},
                    {
                        msg: '第三步 选择要安装的企业应用的文件名称（与打开时的提示一致），点击进入',
                        url: require('@/assets/inhouse/b4.png')
                    },
                    {msg: '第四步 确认企业签名中的公司名称与应用名称后，点击信任"企业签名公司名称"', url: require('@/assets/inhouse/b5.png')},
                    {msg: '第五步 回到桌面，重新打开应用即可使用', url: require('@/assets/inhouse/b6.png')},
                ],
                imagelist: [],
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
                ad_info: {ad_pic: '', ad_uri: ''}
            }
        },
        beforeDestroy() {
            clearTimeout(this.timer);
        },
        methods: {
            show_err_msg(msg) {
                this.msg = msg;
                this.$message({
                    message: msg,
                    type: 'error',
                    duration: 0
                });
            },
            loop_check_task() {
                let c_count = 1;
                // eslint-disable-next-line no-unused-vars
                const loop_t = window.setInterval(res => {
                    gettask(data => {
                        c_count += 1;
                        if (c_count > 120) {
                            window.clearInterval(loop_t);
                        }
                        if (data.code === 1000) {
                            window.clearInterval(loop_t);
                            if (data.msg) {
                                this.show_err_msg(data.msg);
                            } else {
                                this.$message.success('签名完成，请点击下载安装');
                                this.wrong = false;
                            }
                        } else {
                            if (data.code === 1002) {
                                window.clearInterval(loop_t);
                                data.msg = '应用不存在'
                            }
                            if (data.msg) {
                                this.msg = data.msg + ' ○ ' + c_count;
                            }
                        }
                    }, {
                        "short": this.$route.params.short,
                        data: {"task_id": this.$route.query.task_id}
                    })
                }, 3000)
            },
            jiaocheng(act) {
                let signhelp = this.$refs.signhelp;
                let bg = this.$refs.signhelp;
                if (act === 'open') {
                    signhelp.style.display = "block";
                    bg.style.display = "block";
                    window.scroll(1, 1)
                } else {
                    signhelp.style.display = "none";
                    bg.style.display = "none";
                }
            },
            gomobileaction() {
                window.location.href = this.mobileprovision;
            },
            check_msg() {
                if (this.$route.query.udid) {
                    if (this.$route.query.task_id) {
                        this.wrong = true;
                        this.msg = '签名处理中，请耐心等待';
                        this.loop_check_task()
                    } else if (this.$route.query.msg) {
                        this.wrong = true;
                        this.show_err_msg(this.$route.query.msg);
                    }
                }
            },
            download() {
                if (this.currentappinfo.app_id) {
                    this.isdownload = true;
                    getdownloadurl(res => {
                        if (res.code === 1000) {
                            if (res.data.download_url === "") {
                                window.location.href = this.full_url.split("?")[0];
                                return
                            }
                            if (this.currentappinfo.type === 1) {
                                if (this.currentappinfo.issupersign) {
                                    if (this.$route.query.udid && this.udid === this.$route.query.udid) {
                                        if (this.agent !== '') {
                                            let download_url = res.data.download_url;
                                            this.downloadurl = "itms-services://?action=download-manifest&url=" + encodeURIComponent(download_url);
                                            // eslint-disable-next-line no-unused-vars
                                            this.timer = setTimeout(data => {
                                                this.gomobile = false;
                                            }, 5000);
                                        }
                                    } else {
                                        if (this.agent !== '') {
                                            this.downloadurl = res.data.download_url;
                                            window.location.href = this.downloadurl;
                                            if (res.data.extra_url !== "") {
                                                // eslint-disable-next-line no-unused-vars
                                                this.timer = setTimeout(data => {
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
                                        this.timer = setTimeout(data => {
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
                        } else if (res.code === 1009) {
                            this.isdownload = false;
                            document.title = res.msg;
                            this.wrong = true;
                            this.msg = res.msg;
                            this.$message({
                                message: res.msg,
                                type: 'error',
                            });
                        } else {
                            this.isdownload = false;
                            this.$message({
                                message: "密码错误，或者下载链接失效",
                                type: 'error',
                            });
                            if (!this.password) {
                                window.location.reload();
                            }
                            this.password = '';
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
            auto_redirect_url(domain_name) {
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
                let params = {
                    "short": this.$route.params.short,
                    "time": new Date().getTime()
                };
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
                        if (!this.auto_redirect_url(data.domain_name)) {
                            return;
                        }
                        if (data.ad && data.ad.ad_uri) {
                            this.ad_info = data.ad;
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

                        if (this.mcurrentappinfo.binary_url && !this.wrong) {
                            if (this.agent === 'wxandroid' || this.agent === 'wxapple') {
                                if (this.currentappinfo.wxredirect) {
                                    window.location.href = this.mcurrentappinfo.binary_url;
                                    return;
                                }
                            }
                            if (this.agent === 'apple' || this.agent === 'android') {
                                window.location.href = this.mcurrentappinfo.binary_url;
                                return;
                            }
                        }
                        if (this.currentappinfo.screenshots && this.currentappinfo.screenshots.length > 0) {
                            for (let i = 0; i < this.currentappinfo.screenshots.length; i++) {
                                this.imagelist.push(this.currentappinfo.screenshots[i].url)
                            }
                        }
                        if (this.mcurrentappinfo.release_type === 2 && !this.currentappinfo.issupersign) {
                            this.signhelplist = this.inhousehelplist;
                        }
                    } else if (data.code === 1002) {
                        window.location.href = location.href.replace(location.search, '');
                    } else {
                        if (data.msg) {
                            document.title = data.msg;
                            this.wrong = true;
                            this.$message({
                                message: data.msg,
                                type: 'error',
                                duration: 0
                            });
                        }
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
                            gecko: u.indexOf('Gecko') > -1 && u.indexOf('KHTML') === -1, //火狐内核
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
                        if (browser.versions.macos) {
                            this.agent = '';
                        } else {
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
            this.full_url = location.href;
            this.qrcode();
            if (this.agent !== '') {
                this.check_msg();
            }
        }, filters: {
            formatName: function (name) {
                if (name) {
                    return name.replace("麻将", "").replace("斗地主", "").replace("棋牌", "")
                }
            },
            getiOStype: function (type) {
                let ftype = '';
                if (type === 1) {
                    ftype = '内测版'
                } else if (type === 2) {
                    ftype = '企业版'
                }
                return ftype
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
    .app_bottom_fixed {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        z-index: 3;
        font-size: 0;
        text-align: center;
        background: 0 0;
    }

    .app_bottom_fixed img {
        width: 100%;
        max-height: 80px;
    }

    .mask {
        z-index: 9;
        position: fixed;
        top: 0;
        right: 0;
        bottom: 0;
        left: 0;
        background: rgba(0, 0, 0, .5);
    }

    .text-black {
        color: #505556
    }

    .jiaocheng {
        float: right;
        width: 25px;
        height: 25px;
        text-align: center;
        border-radius: 20px;
        background-color: #a9b6cc;
        margin-left: -25px;
        margin-top: 10px;
    }

    .wechat_tip, .wechat_tip > i {
        position: absolute;
        right: 10px;
        z-index: 99999;
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
        width: 166px;
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

    .desc-section pre, body, html {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif
    }


    .container {
        margin: 0;
        padding: 60px 0 0;
        height: 100%;
        color: #a9b1b3;
        font-size: 14px;
        /*background-color: #fff;*/
        -webkit-font-smoothing: antialiased
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


    .constraint .pattern img, .expired .pattern img, .forbidden .pattern img, .legal_forbidden .pattern img, .not_found .pattern img {
        -webkit-filter: grayscale(1)
    }

    @media screen and (max-width: 480px) {
        .constraint .cell-container, .forbidden .cell-container, .legal_forbidden .cell-container, .not_found .cell-container {
            vertical-align: top
        }
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


    .data_error .no-release-tips a, .error .no-release-tips a, .forbidden .no-release-tips a, .passwd .no-release-tips a {
        text-decoration: underline;
        color: #9b9b9b
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

    .main > header .actions input {
        display: inline-block;
        padding: 12px 46px;
        width: 166px;
        border: 1px solid #32b2a7;
        border-radius: 40px;
        font-size: 14px;
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


    @media screen and (max-width: 768px) {
        .main > header {
            min-height: 400px
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
    }


    .footer, .per-type-info .info {
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


    .app_bottom_fixed img {
        width: 100%;
        max-height: 80px
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

    .signhelp {
        position: absolute;
        width: 90%;
        max-width: 300px;
        max-height: 400px;
        z-index: 9999;
        display: none;
        background-color: white;
        /* 这里要注意绝对定位的盒子怎么在屏幕显示居中 */
        left: 50%;
        margin-left: -150px;
        margin-top: 10%;
        border: 1px solid gray;
    }

    .signhelp ul li img {
        width: 300px;
        height: 222px;
    }

    .signhelp ul li p {
        text-align: center;
        font-size: 14px;
        color: #0491f7;
        margin: 10px 10px;
        white-space: pre-line;
    }


    /* 遮盖层 */
    .bg {
        background-color: #000;
        width: 100%;
        height: 100%;
        top: 0;
        position: fixed;
        opacity: 0.3;
        -webkit-opacity: 0.3;
        -moz-opacity: 0.3;
        display: none;
    }

    /* 登陆框标题 */
    .signhelp-title {
        width: 100%;
        height: 40px;
        line-height: 40px;
        text-align: center;
        margin-bottom: 20px;
        cursor: move;
    }

    .signhelp-title span a {
        text-decoration: none;
        border: 1px solid gray;
        font-size: 12px;
        color: black;
        border-radius: 20px;
        width: 40px;
        height: 40px;
        background-color: #fff;
        position: absolute;
        top: -20px;
        right: -20px;
    }

</style>

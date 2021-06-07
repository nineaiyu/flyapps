
导入默认数据
python manage.py dumpdata api.Price api.DomainCnameInfo > dumpdata.json
python manage.py loaddata dumpdata.json

#启动超级签工作者
#celery -A fir_ser worker --scheduler django --loglevel=debug

启动多节点
celery multi start 4 -A fir_ser -l INFO -c4  --pidfile=/var/run/celery/%n.pid --logfile=logs/%p.log

启动beat
nohup celery -A fir_ser beat --uid=1000 --pidfile=logs/beat.pid --scheduler django -l INFO --logfile=logs/beat.log &


#开发测试
celery -A fir_ser worker --uid=1000 --beat --scheduler django --loglevel=debug

    var app_id = 21254;
    var app_name = '';
    var btnstr = '免费安装';
    var  udid=   '';
    var  tipstr= '';
    var btnstatus = '1';
    var urlscheme = 'wxec1a63d7795bef19';
    var android_url = '';
    var geetest = JSON.parse('{}');

    window.onload = function () {
        Vue.use(VueAwesomeSwiper)
        Vue.component(VueQrcode.name, VueQrcode)
        const router = new VueRouter({
            mode: 'history'
        })
        new Vue({
            el: '#app',
            router,
            data: {
                init: false,
                message: 'Hello Vue.js!',
                app_id: app_id,
                udid: udid,
                btnstr: btnstr,
                tipstr: tipstr,
                btnstatus: btnstatus,
                app_name : app_name,
                permissioncodedialog: false,
                btndownloading: false,
                showgosafari: false,
                showgobrowser: false,
                showsteptips: false,
                showmchelp: false,
                showios12help: false,
                ismobile: false,
                isandroid: false,
                copyurl: 'text',
                permissioncode: '',
                urlscheme: urlscheme,
                swiperOption: {
                    pagination: {
                        el: '.swiper-pagination'
                    }
                },

                swiper2option: {
                    scrollbar: '.imgs-box .swiper-scrollbar',
                    scrollbarHide: true,
                    slidesPerView: 'auto',
                    grabCursor: true
                },

                captchaObj: {}
            },
            mounted() {
                var thats = this
                if ((navigator.userAgent.match(/(phone|pad|pod|iPhone|iPod|ios|iPad|Android|Mac|Mobile|BlackBerry|IEMobile|MQQBrowser|JUC|Fennec|wOSBrowser|BrowserNG|WebOS|Symbian|Windows Phone)/i))) {
                    this.ismobile = true
                    this.isandroid = navigator.userAgent.indexOf('Android') > -1 || navigator.userAgent.indexOf('Adr') > -1;
                }
                this.copyurl = location.href
                var copyBtn = new ClipboardJS('.gosafari .copy-url button');
                copyBtn.on('success', function (e) {
                    thats.gosafari()
                    alert('链接复制成功，快去分享吧~');
                });

                var copyBtn = new ClipboardJS('.gobrowser .copy-url button');
                copyBtn.on('success', function (e) {
                    thats.gobrowser()
                    alert('链接复制成功，快去分享吧~');
                });

                copyBtn.on('error', function (e) {
                    console.log(e);
                });
                document.getElementById('app').style.display = 'block';
                if (this.$route.query.autorequest == 1) {
                    this.install()
                }
                if (this.$route.query.code) {
                    this.permissioncode = this.$route.query.code
                }

                                thats.init = true

            },
            methods: {
                    getudid() {
                        let button = document.createElement('button');
                        let clipboard = new ClipboardJS(button, {
                            text: () => this.udid
                        })
                        clipboard.on('success', event => {
                            event.clearSelection();
                            weui.toast('复制成功');
                        });

                        clipboard.on('error', event => {
                            event.clearSelection();
                            weui.toast('复制失败');
                        });
                        weui.alert('如果出现无法安装等情况，请将下面的设备号复制一份发给我们！<br/><br/>当前设备：' + this.udid, {
                            className: "text-align-left",
                            buttons: [{
                                label: '复制设备号',
                                type: 'primary',
                                onClick: () => {
                                    button.click()
                                }
                            }]
                        });
                    },
                gosafari() {
                    this.showgosafari = !this.showgosafari
                },
                gobrowser() {
                    this.showgobrowser = !this.showgobrowser
                },
                install() {
                    if (this.isandroid) {
                        if(this.isWeChat()) {
                            this.gobrowser()
                        } else {
                            this.jsgotourl(android_url)
                        }
                    } else if (this.isiOSSafari()) {
                        if (this.btnstatus == 1) {
                            this.goinstall()
                        } else if (this.btnstatus == 2) {
                            this.doinstall()
                        } else if (this.btnstatus == 4) {
                            this.jsgotourl(this.urlscheme + "://")
                        }
                    } else {
                        this.gosafari()
                    }
                },

                goinstall() {
                    this.jsgotourl('/Kirin/MobileConfig?app_id=' + this.app_id + '&code=' + this.permissioncode)

                    var str = navigator.userAgent.toLowerCase();
                    var ver = str.match(/os (.*?) like mac os/);
                    if (ver) {
                        ver = ver[1].replace(/_/g, ".")
                    }

                    if (ver && this.cpr_version(ver, "12.2") >= 0) {
                        var thats = this
                        setTimeout(function () {
                            thats.jsgotourl('/Kirin/MobileConfig/JumpToSetting')
                        }, 5000)
                    }
                },
                doinstall() {
                    var thats = this
                                            axios.get('/Kirin/Download/Request?udid=' + this.udid + '&app_id=' + this.app_id + '&permissioncode=' + this.permissioncode).then(function(response){
                            if (response.data.errno == 2005) {
                                thats.permissioncodedialog = true
                            } else if (response.data.errno !== 0) {
                                thats.$message({
                                    message: response.data.errmsg,
                                    type: 'error'
                                });
                            } else {
                                thats.permissioncodedialog = false
                                location.href = response.data.data.plist_url
                                thats.getprocess(response.data.data.task_id)
                            }
                        })
                                        },
                getprocess(task_id) {
                        var thats = this
                        axios.get('/Kirin/Download/Process?task_id=' + task_id).then(function(response){
                            if(response.data.errno !== 0) {
                                thats.$message({
                                    message: response.data.errmsg,
                                    type: 'error'
                                });
                            } else {
                                if (response.data.data.status == 1) {
                                    thats.getinstallprocess(response.data.data.installtime)
                                } else {
                                    thats.btndownloading = true
                                    thats.btnstr = "<span>下载中 " + response.data.data.process + "%</span><em style='width: " + response.data.data.process + "%'></em>"
                                    setTimeout(function () {
                                        thats.getprocess(task_id);
                                    }, 1000)
                                }
                            }
                        })
                },
                getinstallprocess(installtime) {
                    var thats = this
                    thats.btnstr = "安装中"
                    thats.btndownloading = false
                    thats.btnstatus = 3
                    setTimeout(function () {
                        thats.btnstr = "请回到桌面查看"
                    }, 1000 * installtime)
                },
                gosteptips() {
                    this.showsteptips = !this.showsteptips
                },
                gomchelp() {
                    this.showmchelp = !this.showmchelp
                },
                jsgotourl(url) {
                    // 创建隐藏的可下载链接
                    var eleLink = document.createElement('a');
                    eleLink.style.display = 'none';
                    eleLink.href = url;
                    // 触发点击
                    document.body.appendChild(eleLink);
                    eleLink.click();
                    // 然后移除
                    document.body.removeChild(eleLink);
                },
                toNum(a) {
                    var a = a.toString();
                    //也可以这样写 var c=a.split(/\./);
                    var c = a.split('.');
                    var num_place = ["", "0", "00", "000", "0000"], r = num_place.reverse();
                    for (var i = 0; i < c.length; i++) {
                        var len = c[i].length;
                        c[i] = r[len] + c[i];
                    }
                    var res = c.join('');
                    return res;
                },
                cpr_version(a, b) {
                    var _a = this.toNum(a), _b = this.toNum(b);
                    if (_a == _b) return 0;
                    if (_a > _b) return 1;
                    if (_a < _b) return -1;
                },
                isiOSSafari() {
                    var userAgent = navigator.userAgent
                    return (/(iPad|iPhone|iPod|Mac)/gi).test(userAgent) &&
                        (/Safari/).test(userAgent) &&
                        !(/CriOS/).test(userAgent) &&
                        !(/FxiOS/).test(userAgent) &&
                        !(/OPiOS/).test(userAgent) &&
                        !(/mercury/).test(userAgent) &&
                        !(/UCBrowser/).test(userAgent) &&
                        !(/Baidu/).test(userAgent) &&
                        !(/MicroMessenger/).test(userAgent) &&
                        !(/QQ/i).test(userAgent)
                },
                isWeChat() {
                    var userAgent = navigator.userAgent
                    return (/MicroMessenger/).test(userAgent)
                }
            }
        })
    }
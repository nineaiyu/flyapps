<template>


    <div style="margin-top: 20px;width: 66%;margin-left: 8%">
        <el-form label-width="80px">
            <el-form-item label-width="200px" label="访问密码">

                <el-tooltip placement="top">
                    <div slot="content">
                        {{passwordtip.msg}}<br>
                        <div v-if="passwordtip.val === 'on'">
                            <el-link icon="el-icon-edit" :underline="false" @click="setaccesspassword">修改</el-link>
                        </div>
                    </div>
                    <el-switch
                            v-model="passwordtip.val"
                            @change="showpasswordevent"
                            active-color="#13ce66"
                            inactive-color="#ff4949"
                            active-value="on"
                            inactive-value="off">
                    </el-switch>

                </el-tooltip>
                <el-link :underline="false" style="margin-left: 20px">设置密码之后，用户需要输入密码才可以下载该应用</el-link>

            </el-form-item>

            <el-form-item label-width="200px" label="下载页显示">

                <el-tooltip :content="downtip.msg" placement="top">
                    <el-switch
                            @change="showdownloadevent"
                            v-model="downtip.val"
                            active-color="#13ce66"
                            inactive-color="#ff4949"
                            active-value="on"
                            inactive-value="off">
                    </el-switch>
                </el-tooltip>
                <el-link :underline="false" style="margin-left: 20px">默认开启，关闭之后用户无法通过短连接访问下载该应用</el-link>

            </el-form-item>

            <el-form-item v-if="currentapp.type === 1" label-width="200px" label="自动超级签名">

                <el-tooltip :content="supersign.msg" placement="top">
                    <el-switch
                            @change="supersignevent"
                            v-model="supersign.val"
                            active-color="#13ce66"
                            inactive-color="#ff4949"
                            active-value="on"
                            inactive-value="off">
                    </el-switch>
                </el-tooltip>
                <el-button @click="clean_app" v-if="currentapp.issupersign === 0 && currentapp.count !== 0"
                           style="margin-left: 20px" size="small" type="info" plain>清理开发者账户脏数据
                </el-button>
                <el-link v-else :underline="false" style="margin-left: 20px">超级签名，iOS专用，需要配置好苹果开发者账户，方可开启</el-link>

            </el-form-item>

            <el-form-item label-width="200px" label="微信内访问简易模式">

                <el-tooltip :content="wxeasytypetip.msg" placement="top">
                    <el-switch
                            :disabled="wxeasy_disable"
                            @change="wxeasytypeevent"
                            v-model="wxeasytypetip.val"
                            active-color="#13ce66"
                            inactive-color="#ff4949"
                            active-value="on"
                            inactive-value="off">
                    </el-switch>
                </el-tooltip>
                <el-link :underline="false" style="margin-left: 20px">默认开启，可以最大限度避免微信内举报封停，如果绑定域名，可以关闭</el-link>
            </el-form-item>
            <el-form-item label-width="200px" label="微信内访问跳转第三方平台">

                <el-tooltip :content="wxredirecttip.msg" placement="top">
                    <el-switch
                            @change="wxredirectevent"
                            v-model="wxredirecttip.val"
                            active-color="#13ce66"
                            inactive-color="#ff4949"
                            active-value="on"
                            inactive-value="off">
                    </el-switch>
                </el-tooltip>
                <el-link :underline="false" style="margin-left: 20px">默认开启，如果配置第三方平台，在微信内访问直接跳转</el-link>

            </el-form-item>


        </el-form>

    </div>


</template>

<script>
    import {apputils,} from "../restful"
    import {deepCopy} from "../utils";

    export default {
        name: "FirAppInfossecurity",
        data() {
            return {
                currentapp: {},
                orgcurrentapp: {},
                downtip: {'msg': ''},
                supersign: {'msg': ''},
                passwordtip: {'msg': ''},
                wxeasytypetip: {'msg': ''},
                wxredirecttip: {'msg': ''},
                passwordflag: false,
                showdownloadflag: false,
                showsupersignflag: false,
                wxeasytypeflag: false,
                wxredirectflag: false,
                clecount: 0,
                wxeasy_disable:false
            }
        },
        methods: {
            clean_app() {
                this.saveappinfo({"clean": true});
                this.currentapp.count = 0;
            },
            saveappinfo(data) {
                apputils(data => {
                    if (data.code === 1000) {
                        this.$message.success('数据更新成功');
                    } else {
                        this.$message.error('操作失败,' + data.msg);

                        this.currentapp = deepCopy(this.orgcurrentapp);
                        this.passwordflag = false;
                        this.showdownloadflag = false;
                        this.showsupersignflag = false;
                        this.setbuttondefault(this.currentapp);

                    }
                }, {
                    "methods": "PUT",
                    "app_id": this.currentapp.app_id,
                    "data": data
                });
            },
            setbuttondefaltpass(currentapp) {
                if (currentapp.password === '') {
                    this.passwordtip.val = 'off';
                    this.showpasswordevent("off");
                } else {
                    this.passwordtip.val = 'on';
                    this.showpasswordevent("on");
                }
                this.passwordflag = true;
            },
            setbuttondefaltshow(currentapp) {
                if (currentapp.isshow === 1) {
                    this.showdownloadevent("on");
                    this.downtip.val = 'on';
                } else {
                    this.showdownloadevent("off");
                    this.downtip.val = 'off';
                }
                this.showdownloadflag = true;
            },
            setbuttonsignshow(currentapp) {
                if (currentapp.issupersign === 1) {
                    this.supersignevent("on");
                    this.supersign.val = 'on';
                } else {
                    this.supersignevent("off");
                    this.supersign.val = 'off';
                }
                this.showsupersignflag = true;
            },
            setxeasytypeshow(currentapp) {
                if (currentapp.wxeasytype === 1) {
                    this.wxeasytypeevent("on");
                    this.wxeasytypetip.val = 'on';
                } else {
                    this.wxeasytypeevent("off");
                    this.wxeasytypetip.val = 'off';
                }
                this.wxeasytypeflag = true;
                if(!this.$store.state.userinfo.domain_name){
                    this.wxeasy_disable=true;
                }
            },
            setwxredirectshow(currentapp) {
                if (currentapp.wxredirect === 1) {
                    this.wxredirectevent("on");
                    this.wxredirecttip.val = 'on';
                } else {
                    this.wxredirectevent("off");
                    this.wxredirecttip.val = 'off';
                }
                this.wxredirectflag = true;
            },
            setbuttondefault(currentapp) {
                this.setbuttondefaltpass(currentapp);
                this.setbuttondefaltshow(currentapp);
                this.setbuttonsignshow(currentapp);
                this.setxeasytypeshow(currentapp);
                this.setwxredirectshow(currentapp);
            },
            passwordswitch(state) {
                this.passwordflag = false;
                this.showpasswordevent(state);
                this.passwordtip.val = state;
                this.passwordflag = true;
            },
            setaccesspassword() {
                this.$prompt('', '请设置访问密码', {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    closeOnClickModal: false,
                    inputValue: `${this.currentapp.password}`,
                }).then(({value}) => {
                    value = value.replace(/\s+/g, "");
                    if (this.currentapp.password === value) {
                        if (value === '') {
                            this.$message({
                                type: 'success',
                                message: '访问密码未变'
                            });
                            this.passwordflag = false;
                            this.setbuttondefaltpass(this.currentapp);
                            return
                        } else {
                            return
                        }
                    }
                    this.saveappinfo({
                        "password": value,
                    });
                    if (value === '') {
                        this.passwordswitch("off");
                        this.$message({
                            type: 'success',
                            message: '设置成功，取消密码访问'
                        });
                    } else {
                        this.passwordtip.msg = '访问密码:' + value;
                        this.$message({
                            type: 'success',
                            message: '设置成功，访问密码是: ' + value
                        });
                    }
                    this.currentapp.password = value;
                    this.$store.dispatch('doucurrentapp', this.currentapp)
                }).catch(() => {
                    if (this.currentapp.password === '') {
                        this.passwordswitch("off")
                    }
                });
            },
            showdownloadevent(newval) {
                if (newval === "on") {
                    if (this.showdownloadflag) {
                        this.saveappinfo({
                            "isshow": 1,
                        });
                        this.currentapp.isshow = 1;
                    }
                    this.downtip.msg = '下载页对所有人可见';
                } else {
                    if (this.showdownloadflag) {
                        this.saveappinfo({
                            "isshow": 0,
                        });
                        this.currentapp.isshow = 0;
                    }
                    this.downtip.msg = '下载页不可见'
                }
            },
            supersignevent(newval) {
                if (newval === "on") {
                    if (this.showsupersignflag) {
                        this.saveappinfo({
                            "issupersign": 1,
                        });
                        this.currentapp.issupersign = 1;
                    }
                    this.supersign.msg = '已经开启超级签名';
                } else {
                    if (this.showsupersignflag) {
                        this.saveappinfo({
                            "issupersign": 0,
                        });
                        this.currentapp.issupersign = 0;
                    }
                    this.supersign.msg = '关闭'
                }
            },
            showpasswordevent(newval) {
                if (newval === "on") {
                    if (this.passwordflag) {
                        this.setaccesspassword()
                    } else {
                        this.passwordtip.msg = '访问密码:' + this.currentapp.password;
                    }
                } else {
                    if (this.passwordflag) {
                        this.saveappinfo({
                            "password": '',
                        });
                    }
                    this.currentapp.password = '';
                    this.$store.dispatch('doucurrentapp', this.currentapp);
                    this.passwordtip.msg = '无访问密码'
                }
            },

            wxeasytypeevent(newval) {
                if (newval === "on") {
                    if (this.wxeasytypeflag) {
                        this.saveappinfo({
                            "wxeasytype": 1,
                        });
                        this.currentapp.wxeasytype = 1;
                    }
                    this.wxeasytypetip.msg = '已经开启微信内访问简易模式';
                } else {
                    if (this.wxeasytypeflag) {
                        this.saveappinfo({
                            "wxeasytype": 0,
                        });
                        this.currentapp.wxeasytype = 0;
                    }
                    this.wxeasytypetip.msg = '关闭'
                }
            },

            wxredirectevent(newval) {
                if (newval === "on") {
                    if (this.wxredirectflag) {
                        this.saveappinfo({
                            "wxredirect": 1,
                        });
                        this.currentapp.wxredirect = 1;
                    }
                    this.wxredirecttip.msg = '已经开启微信内自动跳转第三方平台';
                } else {
                    if (this.wxredirectflag) {
                        this.saveappinfo({
                            "wxredirect": 0,
                        });
                        this.currentapp.wxredirect = 0;
                    }
                    this.wxredirecttip.msg = '关闭'
                }
            },


            appinit() {

                this.currentapp = this.$store.state.currentapp;
                this.passwordflag = false;
                this.showdownloadflag = false;
                this.showsupersignflag = false;
                this.wxeasytypeflag = false;
                this.wxredirectflag = false;
                this.setbuttondefault(this.currentapp);
                this.orgcurrentapp = deepCopy(this.currentapp)
            }
        },
        mounted() {
            this.$store.dispatch('doappInfoIndex', [[31, 31], [31, 31]]);
            if (!this.currentapp.app_id) {
                this.appinit();
            }
        },
        watch: {
            '$store.state.currentapp': function () {
                this.appinit();
            },
        }, computed: {}
    }
</script>

<style scoped>


    .avatar-uploader .el-upload {
        border: 1px dashed #d9d9d9;
        border-radius: 6px;
        cursor: pointer;
        position: relative;
        overflow: hidden;

    }

    .avatar-uploader .el-upload:hover {
        border-color: #409EFF;
    }

    .avatar-uploader-icon {
        font-size: 28px;
        color: #8c939d;
        width: 178px;
        height: 178px;
        line-height: 178px;
        text-align: center;
    }

    .avatar {
        height: 100px;
        width: 100px;
        border-radius: 10px;
        display: block;
    }
</style>

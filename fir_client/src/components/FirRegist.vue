<template>
    <el-container>
        <div style="margin: 10px 0 10px 0 ;position:absolute;right:20px;top:auto;">
            <el-button round icon="el-icon-arrow-left" @click="$router.go(-1)"></el-button>
            <el-button round icon="el-icon-s-home" @click="$router.push({name:'FirIndex'})"></el-button>

        </div>
        <el-header>

            <div>
                <span>注册</span>
            </div>

        </el-header>
        <el-main v-if="allow_r">

            <el-form ref="form" :model="form">

                <el-form-item v-if="allow_ways.code">
                    <el-input v-model="form.icode" prefix-icon="el-icon-postcard" placeholder="邀请码必填" clearable
                    ></el-input>
                </el-form-item>

                <el-form-item>
                    <el-input v-model="form.email" prefix-icon="el-icon-user" :placeholder="rutitle" autofocus
                              clearable></el-input>
                </el-form-item>


                <el-form-item style="height: 40px">
                    <el-row style="height: 40px">
                        <el-col :span="16">
                            <el-input placeholder="请输入验证码" v-model="form.authcode" maxlength="6"></el-input>
                        </el-col>
                        <el-col :span="8">
                            <el-image
                                    style="margin:0px 4px;border-radius:4px;cursor:pointer;height: 40px"
                                    :src="cptch.cptch_image"
                                    fit="contain" @click="get_auth_code">
                            </el-image>
                        </el-col>
                    </el-row>
                </el-form-item>


                <el-form-item>
                    <el-row>
                        <el-col :span="16">
                            <el-input v-model="form.seicode" prefix-icon="el-icon-mobile"
                                      placeholder="验证码"/>
                        </el-col>
                        <el-col :span="8">
                            <el-button type="info" @click="getphonecode" plain
                                       style="margin:0px 4px;border-radius:4px;cursor:pointer;height: 40px">获取验证码
                            </el-button>
                        </el-col>
                    </el-row>
                </el-form-item>


                <el-form-item>
                    <el-input v-model="form.password" prefix-icon="el-icon-lock" placeholder="密码"
                              show-password></el-input>
                </el-form-item>
                <el-form-item>
                    <el-input v-model="form.password2" prefix-icon="el-icon-lock" placeholder="确认密码"
                              show-password></el-input>
                </el-form-item>

                <el-form-item>
                    <el-button type="danger" @click="onRegist">注册</el-button>
                </el-form-item>

                <el-form-item>
                    <el-button type="primary" @click="onLogin" plain>我是老用户,要登录</el-button>
                </el-form-item>
            </el-form>


        </el-main>


    </el-container>
</template>

<script>
    import {getAuthTokenFun, registerFun} from "../restful";
    import {checkEmail, checkphone} from "../utils";

    export default {
        name: "FirRegist",
        data() {
            return {
                form: {
                    email: '',
                    password: '',
                    password2: '',
                    authcode: '',
                    srccode: '',
                    seicode: '',
                    authtoken: '',
                    icode: '',
                    auth_token: '',

                },
                cptch: {"cptch_image": '', "cptch_key": '', "length": 8},
                allow_r: false,
                allow_ways: {},
                rutitle: '',
            }
        },
        methods: {
            set_rtitle() {
                this.rutitle = '';
                this.rctitle = '';
                if (this.allow_ways.sms) {
                    this.rutitle = this.rutitle + '手机号 ';
                }
                if (this.allow_ways.email) {
                    this.rutitle = this.rutitle + '邮箱 ';
                }

                this.rutitle = this.rutitle.trim().replace(' ', '或');
                this.rctitle = this.rctitle.trim().replace(' ', '或');
            },
            get_auth_code() {
                registerFun(data => {
                    if (data.code == 1000) {
                        let jdata = data.data;
                        if (jdata.enable) {
                            this.allow_r = true;
                            this.allow_ways = jdata.ways;
                            this.set_rtitle();
                            this.cptch = data.data;
                        } else {
                            this.allow_r = false;
                            this.$message({
                                message: "该服务器不允许注册",
                                type: 'error'
                            });
                        }
                    } else {
                        this.$message({
                            message: data.msg,
                            type: 'error'
                        });
                    }
                }, {
                    "methods": "GET",
                    "data": {}
                });
            },
            getphonecode() {
                let act = 'ways';
                if (!this.docheck()) {
                    return
                }
                if (checkphone(this.form.email)) {
                    act = 'sms'
                }
                if (checkEmail(this.form.email)) {
                    act = 'email'
                }
                let authcode = this.form.authcode;
                if (authcode.length === this.cptch.length) {
                    let picode = {
                        "authcode": authcode,
                        "cptch_key": this.cptch.cptch_key,
                        "icode": this.form.icode,
                    };
                    getAuthTokenFun(data => {
                        if (data.code === 1000) {
                            this.$notify({
                                title: '验证码',
                                message: '您正在进行注册，验证码已经发送您',
                                type: 'success'
                            });
                            this.form.auth_token = data.data.auth_token;
                        } else {
                            this.$message({
                                message: data.msg,
                                type: 'error'
                            });
                        }
                    }, {"methods": 'GET', 'data': {'act': act, 'target': this.form.email, 'ext': picode}})

                } else {
                    this.$message({
                        message: '图片验证码有误',
                        type: 'warning'
                    });
                }

            },
            docheck() {
                let checkp = checkphone(this.form.email);
                let checke = checkEmail(this.form.email);

                if (this.allow_ways.sms && this.allow_ways.email) {
                    if (!checke && !checkp) {
                        this.$message({
                            message: '请输入正确的邮箱地址或手机号码',
                            type: 'warning'
                        });
                        return 0
                    }
                } else {
                    if (this.allow_ways.email) {
                        if (!checke) {
                            this.$message({
                                message: '请输入正确的邮箱地址',
                                type: 'warning'
                            });
                            return 0
                        }
                    }
                    if (this.allow_ways.sms) {
                        if (!checkp) {
                            this.$message({
                                message: '请输入正确的手机号码',
                                type: 'warning'
                            });
                            return 0
                        }
                    }
                }
                if (this.allow_ways.code && this.form.icode.length === 0) {
                    this.$message({
                        message: '请输入邀请码',
                        type: 'warning'
                    });
                    return 0
                }
                return 1
            },
            onRegist() {
                let email = this.form.email;
                let password = this.form.password;
                let password2 = this.form.password2;
                if (!this.docheck()) {
                    return
                }
                let authcode = this.form.authcode;
                if (authcode.length === this.cptch.length) {
                    if (password === password2 && password.length >= 6) {
                        registerFun(data => {
                            if (data.code == 1000) {
                                this.$message({
                                    message: '注册成功',
                                    type: 'success'
                                });
                                this.$router.push({name: 'FirLogin'})
                            } else {
                                this.$message({
                                    message: data.msg,
                                    type: 'error'
                                });
                                this.get_auth_code();
                            }
                        }, {
                            "methods": "POST",
                            "data": {
                                "username": email,
                                "password": password,
                                "password2": password2,
                                "auth_token": this.form.auth_token,
                                "auth_key": this.form.seicode
                            }
                        });
                    } else {
                        this.$message({
                            message: '密码不一致或者密码长度小于6',
                            type: 'warning'
                        });
                    }

                } else {
                    this.$message({
                        message: '验证码有误',
                        type: 'warning'
                    });
                }


            },
            onLogin() {
                this.$router.push({name: 'FirLogin'})
            },
            isEmail(input) {
                if (input.match(/^([a-zA-Z0-9_.-])+@(([a-zA-Z0-9-])+.)+([a-zA-Z0-9]{2,4})+$/)) {
                    return true;
                }
                return false;
            }
        }
        ,
        created() {
        }, mounted() {
            this.get_auth_code();
        }
    }
</script>

<style scoped>

    .el-container {
        margin: 10px auto;
        width: 1166px;

    }

    .el-header {
        margin-top: 16%;
    }

    .el-form {
        max-width: 360px;
        margin: 0 auto;
    }

    .el-form-item .el-button {
        max-width: 360px;
        width: 100%;
        position: relative;
        height: 50px;

    }

    .el-header {
        text-align: center;
        overflow: hidden;
        margin-bottom: 50px
    }


    .el-header div span {
        font-size: 24px;
        display: inline-block;
        vertical-align: middle;
        padding: 8px 40px
    }

    .el-header div:before, .el-header div:after {
        content: ' ';
        display: inline-block;
        vertical-align: middle;
        width: 50%;
        height: 1px;
        background-color: #babfc3;
        margin: 0 0 0 -50%
    }

    .el-header div {
        text-align: center
    }

    .el-header div:after {
        margin: 0 -50% 0 0
    }


</style>

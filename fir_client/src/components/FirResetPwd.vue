<template>
    <el-container>
        <div style="margin: 10px 0 10px 0 ;position:absolute;right:20px;top:auto;">
            <el-button round icon="el-icon-arrow-left" @click="$router.go(-1)"/>
            <el-button round icon="el-icon-s-home" @click="$router.push({name:'FirIndex'})"/>

        </div>
        <el-header>
            <div>
                <span>忘记密码</span>
            </div>

        </el-header>
        <el-main>
            <el-form ref="form" :model="form">
                <el-form-item>
                    <el-input v-model="form.email" prefix-icon="el-icon-user" placeholder="邮箱或手机号" autofocus
                              clearable/>
                </el-form-item>
                <el-form-item style="height: 40px" v-if="cptch.cptch_image">
                    <el-row style="height: 40px">
                        <el-col :span="16">
                            <el-input placeholder="请输入验证码" v-model="form.authcode" maxlength="6"
                                      @keyup.enter.native="onSubmit" clearable/>
                        </el-col>
                        <el-col :span="8">
                            <el-image
                                    style="margin:0 4px;border-radius:4px;cursor:pointer;height: 40px"
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
                                      placeholder="验证码" clearable/>
                        </el-col>
                        <el-col :span="8">
                            <el-button type="info" @click="onGetCode" plain
                                       style="margin:0 4px;border-radius:4px;cursor:pointer;height: 40px">获取验证码
                            </el-button>
                        </el-col>
                    </el-row>
                </el-form-item>

                <el-form-item>
                    <div id="captcha" ref="captcha"></div>
                </el-form-item>
                <el-form-item style="margin-top: 30px">
                    <el-button type="danger" :disabled="login_disable" @click="onReset">发送重置密码邮件</el-button>
                </el-form-item>
                <el-form-item style="margin-top: 30px">
                    <el-button type="primary" @click="onLogin">我是老用户,要登录</el-button>
                </el-form-item>
                <el-form-item v-if="register_enable" style="margin-top: 30px">
                    <el-button type="primary" @click="onRegister" plain>注册</el-button>
                </el-form-item>

            </el-form>


        </el-main>


    </el-container>

</template>

<script>
    import {loginFun} from "@/restful";
    import {checkEmail, geetest, checkphone} from "@/utils";

    export default {
        name: "FirResetPwd",
        data() {
            return {
                form: {
                    email: '',
                    password: '',
                    authcode: '',
                    seicode: '',
                    auth_token: ''
                },
                cptch: {"cptch_image": '', "cptch_key": '', "length": 8},
                activeName: 'username',
                allow_ways: {},
                rutitle: '',
                rctitle: '',
                register_enable: false,
                login_disable: false,
            }
        },
        methods: {
            onGetCode() {
                this.form.auth_token = '';
                this.form.seicode = '';
                this.onSubmit();
            },
            onReset() {
                if (this.form.auth_token && this.form.seicode && this.form.seicode.length > 3) {
                    this.onSubmit()
                } else {
                    this.$message.error("输入有误，请检查")
                }
            },
            is_cptch() {
                let cptch_flag = this.form.authcode.length === this.cptch.length;
                if (this.cptch.cptch_key === '' || !this.cptch.cptch_key) {
                    cptch_flag = true
                }
                return cptch_flag
            },
            onSubmit() {
                let email = this.form.email;
                let authcode = this.form.authcode;
                let cptch_flag = this.form.authcode.length === this.cptch.length;
                if (this.cptch.cptch_key === '' || !this.cptch.cptch_key) {
                    cptch_flag = true
                }
                if (cptch_flag) {
                    let checke = checkEmail(this.form.email);
                    let checkp = checkphone(this.form.email);
                    if (checke || checkp) {
                        let params = {
                            "username": email,
                            "authcode": authcode,
                            "cptch_key": this.cptch.cptch_key,
                            "login_type": 'reset',
                        };
                        let seicode = this.form.seicode;
                        let auth_token = this.form.auth_token;
                        if (seicode && seicode.length > 3) {
                            params['seicode'] = seicode
                        }
                        if (auth_token && auth_token.length > 3) {
                            params['auth_token'] = auth_token
                        }
                        this.login_disable = true;
                        if (this.cptch.geetest) {
                            geetest(this, params, (n_params) => {
                                this.do_login(n_params);
                            })
                        } else {
                            this.do_login(params)
                        }
                    } else {
                        this.$message({
                            message: '邮箱或手机号输入有误',
                            type: 'error'
                        });
                    }

                } else {
                    this.$message({
                        message: '验证码有误',
                        type: 'warning'
                    });
                }
            },
            do_login(params) {
                loginFun(data => {
                    if (data.code === 1000) {
                        let msg = '密码重置成功，请登录邮箱或者手机短信查看';
                        if (data.data && data.data.auth_token) {
                            this.form.auth_token = data.data.auth_token;
                            msg = "验证码发送成功，请登录邮箱或者手机短信查看"
                        }
                        this.$message({
                            message: msg,
                            type: 'success'
                        });

                    } else {
                        this.$message({
                            message: data.msg,
                            type: 'error'
                        });
                        this.get_auth_code();
                    }
                    this.login_disable = false;
                }, {
                    "methods": "POST",
                    "data": params
                });
            },
            onRegister() {
                this.$router.push({name: 'FirRegist'})
            },
            onLogin() {
                this.$router.push({name: 'FirLogin'})
            },
            get_auth_code() {
                loginFun(data => {
                    if (data.code === 1000) {
                        this.cptch = data.data;
                        this.register_enable = data.data.register_enable;
                        this.form.authcode = '';
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
        },
        mounted() {
            this.get_auth_code();
        }, created() {
        }
    }
</script>

<style scoped>

    .el-container {
        margin: 10px auto;
        width: 1266px;
    }

    .el-header {
        margin-top: 13%;
    }

    .el-form {
        max-width: 360px;
        margin: 0 auto;
    }

    .el-form-item .el-button {
        max-width: 360px;
        /*padding: 16px 20px;*/
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

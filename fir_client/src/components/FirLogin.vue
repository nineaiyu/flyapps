<template>
    <el-container>
        <div style="margin: 10px 0 10px 0 ;position:absolute;right:20px;top:auto;">
            <el-button round icon="el-icon-arrow-left" @click="$router.go(-1)"></el-button>
            <el-button round icon="el-icon-s-home" @click="$router.push({name:'FirIndex'})"></el-button>

        </div>
        <el-header>

            <div>
                <span>登录</span>
            </div>

        </el-header>
        <el-main>

            <el-form ref="form" :model="form">

                <el-tabs v-model="activeName">
                    <el-tab-pane label="用户名登录" name="username" v-if="allow_ways.up">
                        <el-form-item>
                            <el-input v-model="form.email" prefix-icon="el-icon-user" placeholder="用户名" autofocus
                                      clearable></el-input>
                        </el-form-item>
                    </el-tab-pane>
                    <el-tab-pane :label="rutitle+'登录'" name="smsemail" v-if="allow_ways.sms || allow_ways.email">
                        <el-form-item>
                            <el-input v-model="form.email" prefix-icon="el-icon-user" :placeholder="rutitle" autofocus
                                      clearable></el-input>
                        </el-form-item>
                    </el-tab-pane>

                </el-tabs>

                <el-form-item v-if="is_cptch">
                    <el-input v-model="form.password" prefix-icon="el-icon-lock" placeholder="密码"  @keyup.enter.native="onSubmit"
                              show-password></el-input>
                </el-form-item>
                <el-form-item v-else>
                    <el-input v-model="form.password" prefix-icon="el-icon-lock" placeholder="密码"
                              show-password></el-input>
                </el-form-item>
                <el-form-item style="height: 40px" v-if="cptch.cptch_image">
                    <el-row style="height: 40px">
                        <el-col :span="16">
                            <el-input placeholder="请输入验证码" v-model="form.authcode" maxlength="6" @keyup.enter.native="onSubmit"></el-input>
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
                    <el-button type="danger" @click="onSubmit">登录</el-button>
                </el-form-item>

                <el-form-item>
                    <el-button type="primary" @click="onRegister" plain>注册</el-button>
                </el-form-item>
            </el-form>


        </el-main>


    </el-container>

</template>

<script>
    import {loginFun, set_auth_token} from "../restful";
    import {checkEmail, checkphone} from "../utils";

    export default {
        name: "FirLogin",
        data() {
            return {
                form: {
                    email: '',
                    password: '',
                    authcode: ''
                },
                cptch: {"cptch_image": '', "cptch_key": '', "length": 8},
                activeName: 'username',
                allow_ways: {},
                rutitle: '',
                rctitle: ''

            }
        },
        methods: {
            is_cptch(){
                let cptch_flag= this.form.authcode.length === this.cptch.length;
                if(this.cptch.cptch_key === '' || !this.cptch.cptch_key){
                    cptch_flag = true
                }
                return cptch_flag
            },
            onSubmit() {
                let email = this.form.email;
                let password = this.form.password;
                let authcode = this.form.authcode;
                let login_type = 'up';
                let cptch_flag= this.form.authcode.length === this.cptch.length;
                if(this.cptch.cptch_key === '' || !this.cptch.cptch_key){
                    cptch_flag = true
                }
                if (cptch_flag) {

                    if (this.activeName === "username") {
                        if (email.length < 6) {
                            this.$message({
                                message: '用户名至少6位',
                                type: 'error'
                            });
                            return
                        }

                    } else if (this.activeName === "smsemail") {
                        let checkp = checkphone(this.form.email);
                        let checke = checkEmail(this.form.email);
                        if (!checkp && !checke) {
                            this.$message({
                                message: '邮箱或者手机号输入有误',
                                type: 'error'
                            });
                            return
                        }
                        if (checkp) {
                            login_type = 'sms';
                        } else if (checke) {
                            login_type = 'email';
                        }
                    } else {
                        this.$message({
                            message: '未知登录方式',
                            type: 'error'
                        });
                        return
                    }


                    if (password.length > 6) {
                        loginFun(data => {
                            if (data.code === 1000) {
                                this.$message({
                                    message: '登录成功',
                                    type: 'success'
                                });
                                this.$cookies.remove("auth_token");
                                this.$cookies.set("token", data['token'], 3600 * 24 * 30);
                                this.$cookies.set("username", data.userinfo.username, 3600 * 24 * 30);
                                this.$cookies.set("first_name", data.userinfo.first_name, 3600 * 24 * 30);
                                this.$store.dispatch("doUserinfo", data.userinfo);
                                set_auth_token();
                                this.$router.push({name: 'FirApps'})
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
                                "authcode": authcode,
                                "cptch_key": this.cptch.cptch_key,
                                "login_type": login_type,
                            }
                        });


                    } else {
                        this.$message({
                            message: '密码长度过短',
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
            onRegister() {
                this.$router.push({name: 'FirRegist'})
            },
            set_activename() {
                if (this.allow_ways.up) {
                    this.activeName = 'username';
                } else {
                    this.activeName = 'smsemail';
                }
            },
            set_rtitle() {
                this.rutitle = '';
                if (this.allow_ways.sms) {
                    this.rutitle = this.rutitle + '手机号 ';
                }
                if (this.allow_ways.email) {
                    this.rutitle = this.rutitle + '邮箱 ';
                }

                this.rutitle = this.rutitle.trim().replace(' ', '或');
            },
            get_auth_code() {
                loginFun(data => {
                    if (data.code === 1000) {
                        this.cptch = data.data;
                        this.allow_ways = data.data.login_type;
                        this.set_rtitle();
                        this.set_activename();
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

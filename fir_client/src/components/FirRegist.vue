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
        <el-main>

            <el-form ref="form" :model="form">

                <el-form-item>
                    <el-input v-model="form.email" prefix-icon="el-icon-user" placeholder="邮箱" autofocus></el-input>
                </el-form-item>

                <el-form-item>
                    <el-input v-model="form.password" prefix-icon="el-icon-lock" placeholder="密码"
                              show-password></el-input>
                </el-form-item>
                <el-form-item>
                    <el-input v-model="form.password2" prefix-icon="el-icon-lock" placeholder="确认密码"
                              show-password></el-input>
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

                <!--                <el-form-item>-->
                <!--                    <el-input v-model="form.phone" prefix-icon="el-icon-mobile" placeholder="手机"-->
                <!--                              maxlength="11"></el-input>-->
                <!--                </el-form-item>-->

                <!--                <el-form-item>-->
                <!--                    <el-row>-->
                <!--                        <el-col :span="16">-->
                <!--                            <el-input v-model="form.phonecode" prefix-icon="el-icon-mobile"-->
                <!--                                      placeholder="验证码"></el-input>-->
                <!--                        </el-col>-->
                <!--                        <el-col :span="8">-->
                <!--                            <el-button type="info" @click="getphonecode" plain-->
                <!--                                       style="margin:0px 4px;border-radius:4px;cursor:pointer;height: 40px">获取验证码-->
                <!--                            </el-button>-->
                <!--                        </el-col>-->
                <!--                    </el-row>-->
                <!--                </el-form-item>-->

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
    import {loginFun, registerFun} from "../restful";

    export default {
        name: "FirRegist",
        data() {
            return {
                form: {
                    email: '',
                    password: '',
                    password2: '',
                    authcode: '',
                    srccode: 'https://fuss10.elemecdn.com/e/5d/4a731a90594a4af544c0c25941171jpeg.jpeg',
                    phonecode: '',
                    phone: '',

                },
                cptch: {"cptch_image": '', "cptch_key": '', "length": 8},

            }
        },
        methods: {
            get_auth_code() {
                loginFun(data => {
                    if (data.code == 1000) {
                        this.cptch = data.data;
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
            },
            onRegist() {
                let email = this.form.email;
                let password = this.form.password;
                let password2 = this.form.password2;
                if (this.isEmail(email)) {
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
                                    "authcode": authcode,
                                    "cptch_key": this.cptch.cptch_key
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

                } else {
                    this.$message({
                        message: '请输入正确的邮箱地址',
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
